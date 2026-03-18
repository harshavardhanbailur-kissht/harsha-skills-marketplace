# Mobile App Development Decision Trees

## Table of Contents

- [1. Framework Selection Decision Tree](#1-framework-selection-decision-tree)
- [2. Architecture Selection Decision Tree](#2-architecture-selection-decision-tree)
- [3. State Management Selection Tree](#3-state-management-selection-tree)
- [4. Navigation Pattern Selection Tree](#4-navigation-pattern-selection-tree)
- [5. Data Storage Selection Tree](#5-data-storage-selection-tree)
- [6. Testing Strategy Selection Tree](#6-testing-strategy-selection-tree)
- [7. Backend/API Architecture Selection Tree](#7-backendapi-architecture-selection-tree)
- [8. Deployment Strategy Selection Tree](#8-deployment-strategy-selection-tree)
- [Decision Tree Usage Guide](#decision-tree-usage-guide)

Strategic decision frameworks for making critical architectural and technology choices in mobile app development. Each tree is designed to be traversed sequentially based on project constraints and team capabilities.

---

## 1. Framework Selection Decision Tree

Choose your primary development framework based on constraints and team composition.

```
START: Building new mobile app?
│
├─ Need multi-platform (iOS + Android) from single codebase?
│  │
│  ├─ YES: Team JavaScript/TypeScript proficient?
│  │  │
│  │  ├─ YES: Can afford Expo managed services ($50+/mo)?
│  │  │  │
│  │  │  ├─ YES: Need native modules/custom bridges?
│  │  │  │  ├─ NO → CHOOSE: Expo managed (fastest iteration, best DX)
│  │  │  │  │          ACTION: `npx create-expo-app`, use Expo Go for testing
│  │  │  │  │
│  │  │  │  └─ YES: Complex native integrations required?
│  │  │  │      ├─ YES → CHOOSE: React Native (Bare) with native modules
│  │  │  │      │          ACTION: `npx react-native@latest init`, set up native toolchains
│  │  │  │      │
│  │  │  │      └─ NO → CHOOSE: Expo + EAS (middle ground)
│  │  │  │          ACTION: `eas build` for cloud builds
│  │  │  │
│  │  │  └─ NO: Team needs instant feedback loop?
│  │  │      ├─ YES → CHOOSE: Expo managed (not cost-prohibitive)
│  │  │      │          ACTION: Use Expo SDK, avoid bare React Native
│  │  │      │
│  │  │      └─ NO → CHOOSE: React Native (Bare) self-hosted
│  │  │          ACTION: Run local builds, EAS Build alternative
│  │  │
│  │  └─ NO: Team knows Dart?
│  │     │
│  │     ├─ YES: Need maximum performance/battery efficiency?
│  │     │  ├─ YES → CHOOSE: Flutter (best performance for 2D apps)
│  │     │  │          ACTION: `flutter create`, set up Android Studio + Xcode
│  │     │  │
│  │     │  └─ NO → CHOOSE: Flutter (developer experience is better)
│  │     │      ACTION: Hot reload, strong async/await support
│  │     │
│  │     └─ NO: Team learns new language quickly?
│  │        ├─ YES: Time/budget for ramp-up (2-4 weeks)?
│  │        │  ├─ YES → CHOOSE: Flutter
│  │        │  │          ACTION: Invest in Dart training, long-term payoff
│  │        │  │
│  │        │  └─ NO → CHOOSE: .NET MAUI (if C# team) or Capacitor
│  │        │      ACTION: MAUI if existing .NET shop, else Capacitor
│  │        │
│  │        └─ NO: Hire specialists or use KMP?
│  │           ├─ HIRE → CHOOSE: Flutter (easier to hire)
│  │           │          ACTION: Recruit Dart developers
│  │           │
│  │           └─ KMP: Team knows Kotlin?
│  │              ├─ YES → CHOOSE: Kotlin Multiplatform (advanced option)
│  │              │          ACTION: Setup KMP project with shared logic
│  │              │
│  │              └─ NO → CHOOSE: Capacitor (web-first approach)
│  │                  ACTION: Build web app, wrap in Capacitor
│  │
│  └─ NO: iOS only OR Android only?
│     │
│     ├─ iOS ONLY: Team knows Swift?
│     │  │
│     │  ├─ YES: Need SwiftUI (2020+) compatibility?
│     │  │  ├─ YES → CHOOSE: Native Swift + SwiftUI
│     │  │  │          ACTION: `xcodegen`, SwiftUI previews, Xcode 14+
│     │  │  │
│     │  │  └─ NO: Support iOS 12-13?
│     │  │      ├─ YES → CHOOSE: Native UIKit
│     │  │      │          ACTION: Support lifecycle, legacy patterns
│     │  │      │
│     │  │      └─ NO → CHOOSE: Native Swift + SwiftUI
│     │  │          ACTION: Minimum iOS 14+, better performance
│     │  │
│     │  └─ NO: Team knows Objective-C?
│     │     ├─ YES → CHOOSE: Objective-C (legacy maintenance)
│     │     │          ACTION: ObjC++, consider modernizing
│     │     │
│     │     └─ NO: Need low latency/GPU work?
│     │        ├─ YES → CHOOSE: Native Swift + Metal
│     │        │          ACTION: High-performance graphics
│     │        │
│     │        └─ NO → CHOOSE: Hire Swift developers
│     │            ACTION: Swift adoption has strong ROI
│     │
│     └─ ANDROID ONLY: Team knows Kotlin?
│        │
│        ├─ YES: Need Compose UI (2021+) compatibility?
│        │  ├─ YES → CHOOSE: Kotlin + Jetpack Compose
│        │  │          ACTION: Modern declarative UI, Material 3
│        │  │
│        │  └─ NO: Support Android 5-7?
│        │      ├─ YES → CHOOSE: Kotlin + XML Layouts + Jetpack
│        │      │          ACTION: View Binding, ViewModel, LiveData
│        │      │
│        │      └─ NO → CHOOSE: Kotlin + Jetpack Compose
│        │          ACTION: API 21+, modern reactive UI
│        │
│        └─ NO: Team knows Java?
│           ├─ YES → CHOOSE: Kotlin (100% interoperable)
│           │          ACTION: Gradual migration possible
│           │
│           └─ NO: PWA acceptable alternative?
│              ├─ YES → CHOOSE: PWA (web technologies)
│              │          ACTION: Progressive Web App, installable
│              │
│              └─ NO → CHOOSE: Hire Kotlin developers
│                  ACTION: Better than Java for modern Android
│
└─ Progressive Web App acceptable?
   │
   ├─ YES: Team knows React/Vue/Angular?
   │  │
   │  ├─ YES: Real offline sync needed?
   │  │  ├─ YES → CHOOSE: Capacitor + React/Vue
   │  │  │          ACTION: Hybrid approach, service workers + native
   │  │  │
   │  │  └─ NO → CHOOSE: Pure PWA
   │  │      ACTION: Add to Home Screen, works offline
   │  │
   │  └─ NO: Budget for web specialist?
   │     ├─ YES → CHOOSE: PWA with new framework
   │     │          ACTION: Svelte/Astro for performance
   │     │
   │     └─ NO → CHOOSE: No-code/low-code platform
   │         ACTION: FlutterFlow, Draftbit, or similar
   │
   └─ NO: Project requires native performance/UX
      └─ NAVIGATE: Return to tree top, choose native
```

---

## 2. Architecture Selection Decision Tree

Select architectural patterns based on project complexity and team constraints.

```
START: Designing app architecture?
│
├─ App complexity level?
│  │
│  ├─ SIMPLE (CRUD app, <10 screens, minimal state):
│  │  │
│  │  ├─ Need future scalability?
│  │  │  ├─ NO → CHOOSE: MVC (Model-View-Controller)
│  │  │  │          ACTION: Simple, direct, works for small apps
│  │  │  │
│  │  │  └─ YES → CHOOSE: MVVM (future-proof)
│  │  │      ACTION: Better separation, easier to expand later
│  │  │
│  │  └─ NEXT: Proceed to State Management tree
│  │
│  ├─ MEDIUM (10-30 screens, complex state, feature flags):
│  │  │
│  │  ├─ Framework choice: React Native/Expo?
│  │  │  │
│  │  │  ├─ YES: Testing requirement HIGH?
│  │  │  │  ├─ YES → CHOOSE: Redux + MVVM pattern
│  │  │  │  │          ACTION: Redux DevTools, time-travel debugging
│  │  │  │  │
│  │  │  │  └─ NO → CHOOSE: Context API + MVVM
│  │  │  │      ACTION: Lighter weight, built-in
│  │  │  │
│  │  │  └─ NO: Flutter selected?
│  │  │     │
│  │  │     ├─ YES: Bloc required by team?
│  │  │     │  ├─ YES → CHOOSE: BLoC pattern (MVVM variant)
│  │  │     │  │          ACTION: flutter_bloc package, events-driven
│  │  │     │  │
│  │  │     │  └─ NO → CHOOSE: Provider + MVVM
│  │  │     │      ACTION: Simpler than BLoC, solid for medium apps
│  │  │     │
│  │  │     └─ NO: Native iOS (Swift)?
│  │  │        │
│  │  │        ├─ YES: iOS 15+?
│  │  │        │  ├─ YES → CHOOSE: MVVM + Combine
│  │  │        │  │          ACTION: Reactive bindings, modern Swift
│  │  │        │  │
│  │  │        │  └─ NO → CHOOSE: MVVM + RxSwift
│  │  │        │      ACTION: Reactive framework
│  │  │        │
│  │  │        └─ NO: Native Android (Kotlin)?
│  │  │           └─ CHOOSE: MVVM + Jetpack (ViewModel + StateFlow)
│  │  │               ACTION: Coroutines + LiveData pattern
│  │  │
│  │  └─ NEXT: Proceed to State Management tree
│  │
│  └─ COMPLEX (30+ screens, real-time sync, offline-first, multiple user types):
│     │
│     ├─ Real-time data requirements?
│     │  │
│     │  ├─ YES: WebSocket/CRDT sync?
│     │  │  ├─ YES → CHOOSE: Clean Architecture + Redux-like pattern
│     │  │  │          ACTION: Domain/Data/Presentation layers, event streaming
│     │  │  │
│     │  │  └─ NO → CHOOSE: TCA (The Composable Architecture) if Swift
│     │  │      ACTION: Modular, testable, reducers pattern
│     │  │
│     │  └─ NO: Offline-first critical?
│     │     │
│     │     ├─ YES: Data sync complexity high?
│     │     │  ├─ YES → CHOOSE: Clean Architecture (max separation)
│     │     │  │          ACTION: Repository pattern, data/domain layers
│     │     │  │
│     │     │  └─ NO → CHOOSE: VIPER (iOS) or MVI (Android)
│     │     │      ACTION: Strict interface-based architecture
│     │     │
│     │     └─ NO: Team >5 developers?
│     │        ├─ YES → CHOOSE: Clean Architecture
│     │        │          ACTION: Clear responsibilities, reduce merge conflicts
│     │        │
│     │        └─ NO → CHOOSE: MVVM with modular features
│     │            ACTION: Lightweight but structured
│     │
│     └─ NEXT: Proceed to State Management tree (complex section)
```

---

## 3. State Management Selection Tree

Choose state management solution based on framework and data complexity.

```
START: Selecting state management?
│
├─ Framework: React Native / Expo?
│  │
│  ├─ YES: App complexity?
│  │  │
│  │  ├─ SIMPLE (useState hooks sufficient):
│  │  │  └─ CHOOSE: React Hooks (Context API if multi-level)
│  │  │      ACTION: useState, useReducer, no external library
│  │  │
│  │  ├─ MEDIUM (multiple feature states, need persistence):
│  │  │  │
│  │  │  ├─ Team knows Redux?
│  │  │  │  ├─ YES → CHOOSE: Redux Toolkit
│  │  │  │  │          ACTION: RTK Query for server state, RTK for client state
│  │  │  │  │
│  │  │  │  └─ NO: Prefer simpler API?
│  │  │  │     ├─ YES → CHOOSE: Zustand
│  │  │  │     │          ACTION: Minimal boilerplate, excellent DX
│  │  │  │     │
│  │  │  │     └─ NO → CHOOSE: Jotai or Recoil
│  │  │  │         ACTION: Atomic state management
│  │  │  │
│  │  │  └─ CHOOSE: MobX (if functional reactive preference)
│  │  │      ACTION: Decorator-based, data-driven reactivity
│  │  │
│  │  └─ COMPLEX (real-time, offline, multi-device sync):
│  │     │
│  │     ├─ Real-time CRDT/OT needed?
│  │     │  ├─ YES → CHOOSE: TanStack Query + custom sync layer
│  │     │  │          ACTION: Server state management first, then custom conflict resolution
│  │     │  │
│  │     │  └─ NO: Complex offline workflows?
│  │     │     ├─ YES → CHOOSE: Redux + Redux Persist + WatermelonDB
│  │     │     │          ACTION: Normalized state, optimistic updates
│  │     │     │
│  │     │     └─ NO → CHOOSE: TanStack Query (server-centric)
│  │     │         ACTION: Powerful caching, background sync, retry logic
│  │     │
│  │     └─ NEXT: Evaluate offline storage separately
│  │
│  └─ PROCEED TO: Framework-specific sections below
│
├─ Framework: Flutter?
│  │
│  ├─ App complexity?
│  │  │
│  │  ├─ SIMPLE (single feature, basic state):
│  │  │  └─ CHOOSE: setState (StatefulWidget)
│  │  │      ACTION: Built-in, minimal overhead
│  │  │
│  │  ├─ MEDIUM (multi-page, shared state between screens):
│  │  │  │
│  │  │  ├─ Team experience with streams?
│  │  │  │  ├─ YES → CHOOSE: Provider package
│  │  │  │  │          ACTION: ChangeNotifier, Consumer widgets
│  │  │  │  │
│  │  │  │  └─ NO: Event-driven preference?
│  │  │  │     ├─ YES → CHOOSE: BLoC (flutter_bloc)
│  │  │  │     │          ACTION: Streams, events, states, bloc pattern
│  │  │  │     │
│  │  │  │     └─ NO → CHOOSE: Riverpod
│  │  │  │         ACTION: Provider successor, better DX, ref-based
│  │  │  │
│  │  │  └─ CHOOSE: GetX (if speed-to-market priority)
│  │  │      ACTION: All-in-one: state, routing, DI
│  │  │
│  │  └─ COMPLEX (real-time features, offline, multiple streams):
│  │     │
│  │     ├─ Need immutable state + freezed?
│  │     │  ├─ YES → CHOOSE: Riverpod + Freezed
│  │     │  │          ACTION: Functional, strongly typed, generates code
│  │     │  │
│  │     │  └─ NO: Heavy event processing?
│  │     │     ├─ YES → CHOOSE: BLoC with Repository pattern
│  │     │     │          ACTION: Event → BLoC → State pipeline
│  │     │     │
│  │     │     └─ NO → CHOOSE: Provider with LocalStorage
│  │     │         ACTION: Lightweight, persistence via hive
│  │
├─ Framework: Native Swift (iOS)?
│  │
│  ├─ iOS deployment minimum?
│  │  │
│  │  ├─ iOS 15+ only:
│  │  │  │
│  │  │  ├─ Preference: Apple frameworks?
│  │  │  │  ├─ YES → CHOOSE: Combine + @Published properties
│  │  │  │  │          ACTION: SwiftUI integration, native ecosystem
│  │  │  │  │
│  │  │  │  └─ NO: Want third-party reactivity?
│  │  │  │     ├─ YES → CHOOSE: SwiftUI + Swift Concurrency
│  │  │  │     │          ACTION: async/await, actors, native concurrency
│  │  │  │     │
│  │  │  │     └─ NO → CHOOSE: RxSwift
│  │  │  │         ACTION: Mature reactive framework
│  │  │  │
│  │  │  └─ CHOOSE: SwiftUI observable macros (iOS 17+)
│  │  │      ACTION: Simplest modern approach
│  │  │
│  │  └─ iOS 13-14 support needed:
│  │     └─ CHOOSE: RxSwift + UIKit/SwiftUI hybrid
│  │         ACTION: Time-tested reactive framework
│  │
│  └─ CHOOSE: MVVM + ObservableObject (for complex scenarios)
│      ACTION: Manual observation with EnvironmentObject
│
└─ Framework: Native Kotlin (Android)?
   │
   ├─ Android target API?
   │  │
   │  ├─ API 21+ (broad reach):
   │  │  │
   │  │  ├─ Using Jetpack Compose?
   │  │  │  ├─ YES → CHOOSE: StateFlow + ViewModel
   │  │  │  │          ACTION: Coroutines-based, Compose-native
   │  │  │  │
   │  │  │  └─ NO: Using XML Layouts?
   │  │  │     └─ CHOOSE: LiveData + ViewModel (traditional)
   │  │  │         ACTION: Stable, lifecycle-aware
   │  │  │
   │  │  └─ CHOOSE: Kotlin Flow + Repository
   │  │      ACTION: More flexible than LiveData
   │  │
   │  └─ API 24+ only:
   │     └─ CHOOSE: StateFlow (modern, Flow-based)
   │         ACTION: Kotlin Coroutines first-class support
   │
   └─ NEXT: Check data persistence separately (Room, Realm, etc.)
```

---

## 4. Navigation Pattern Selection Tree

Choose navigation patterns based on information architecture and user flows.

```
START: Designing navigation pattern?
│
├─ Primary content organization?
│  │
│  ├─ LINEAR / WIZARD-LIKE (step-by-step flow: signup, payment, checkout):
│  │  │
│  │  ├─ Frequent back-navigation?
│  │  │  ├─ YES → CHOOSE: Stack Navigation with backstack management
│  │  │  │          ACTION: React Navigation Stack, Flutter Navigator.push
│  │  │  │
│  │  │  └─ NO: Prevent accidental back, confirm on exit?
│  │  │     └─ CHOOSE: Modal/Dialog stack (disallow pop)
│  │  │         ACTION: Force completion before dismissal
│  │  │
│  │  └─ NEXT: Implement with framework stack navigator
│  │
│  ├─ 2-5 EQUAL PRIMARY SECTIONS (Home, Messages, Account):
│  │  │
│  │  ├─ iOS convention required?
│  │  │  ├─ YES → CHOOSE: Tab Bar Navigation (bottom or top)
│  │  │  │          ACTION: UITabBarController, SwiftUI TabView
│  │  │  │
│  │  │  └─ NO: Android convention required?
│  │  │     │
│  │  │     ├─ YES: Bottom navigation (Google convention)?
│  │  │     │  ├─ YES → CHOOSE: Bottom Navigation Bar
│  │  │     │  │          ACTION: Material 3 NavigationBar, 3-5 items max
│  │  │     │  │
│  │  │     │  └─ NO: Drawer + top nav?
│  │  │     │     └─ CHOOSE: Drawer Navigation
│  │  │     │         ACTION: Hamburger menu, collapsible
│  │  │     │
│  │  │     └─ NO: Cross-platform, independent UI:
│  │  │        ├─ Small screens (phone focus)?
│  │  │        │  ├─ YES → CHOOSE: Bottom Tab Navigation
│  │  │        │  │          ACTION: Touchable, accessible
│  │  │        │  │
│  │  │        │  └─ NO: Tablet/web responsive?
│  │  │        │     └─ CHOOSE: Drawer Navigation (adaptive)
│  │  │        │         ACTION: Drawer on mobile, sidebar on tablet
│  │  │        │
│  │  │        └─ CHOOSE: Top Tab Navigation (scrollable)
│  │  │            ACTION: For 5+ tabs, less ideal for bottom
│  │  │
│  │  └─ NEXT: Each tab contains stack navigator internally
│  │
│  ├─ 6+ PRIMARY SECTIONS or NESTED CATEGORY HIERARCHY:
│  │  │
│  │  ├─ Categories, subcategories, items (e-commerce):
│  │  │  │
│  │  │  ├─ Frequent sibling navigation?
│  │  │  │  ├─ YES → CHOOSE: Drawer + Stack (primary), Stack + Tabs (detail)
│  │  │  │  │          ACTION: Drawer for category, tabs in detail view
│  │  │  │  │
│  │  │  │  └─ NO: Deep drill-down main path?
│  │  │  │     └─ CHOOSE: Single Stack, breadcrumbs in UI
│  │  │  │         ACTION: Linear drill-down, show path at top
│  │  │  │
│  │  │  └─ NEXT: Implement nested navigation architecture
│  │  │
│  │  └─ Master-detail pattern (list + detail pane)?
│  │     │
│  │     ├─ Compact phones only?
│  │     │  └─ CHOOSE: Stack navigation (list → detail modal/push)
│  │     │     ACTION: Stack.Navigator with conditional modals
│  │     │
│  │     └─ Tablet + phone support?
│  │        └─ CHOOSE: Split view (adaptive master-detail)
│  │            ACTION: SplitViewController (iOS), NavigationSuiteScaffold (Android)
│  │
│  └─ OVERLAY / TEMPORARY (modals, bottom sheets, dialogs):
│     │
│     ├─ User action required before proceeding?
│     │  ├─ YES → CHOOSE: Modal (blocks back, focus on task)
│     │  │          ACTION: presentViewController, showDialog
│     │  │
│     │  └─ NO: Can dismiss and continue?
│     │     ├─ YES: Small interaction (confirm, quick input)?
│     │     │  ├─ YES → CHOOSE: Dialog / Alert
│     │     │  │          ACTION: AlertDialog, quick responses
│     │     │  │
│     │     │  └─ NO: Rich content (forms, lists)?
│     │     │     └─ CHOOSE: Bottom Sheet
│     │     │         ACTION: DraggableScrollableSheet (Flutter), BottomSheetDialogFragment
│     │     │
│     │     └─ CHOOSE: Transparent overlay with swipe-to-dismiss
│     │         ACTION: Tap outside to close, gesture support
│     │
│     └─ NEXT: Implement as modal stack on top of main navigation
│
└─ FINAL ACTION: Combine selections into composite navigation
   Example: Tab Navigation + Stack per tab + Modal overlay
   Implementation: React Navigation structure / Flutter Navigator nesting
```

---

## 5. Data Storage Selection Tree

Choose persistence layer based on data complexity and sync requirements.

```
START: Evaluating local data storage?
│
├─ Data complexity?
│  │
│  ├─ SIMPLE (key-value, preferences, tokens):
│  │  │
│  │  ├─ Security-sensitive (tokens, passwords)?
│  │  │  ├─ YES: Platform?
│  │  │  │  ├─ iOS → CHOOSE: Keychain via SecureEnclave
│  │  │  │  │          ACTION: KeychainAccess, use kSecClassGenericPassword
│  │  │  │  │
│  │  │  │  ├─ Android → CHOOSE: EncryptedSharedPreferences (Jetpack)
│  │  │  │  │          ACTION: androidx.security:security-crypto
│  │  │  │  │
│  │  │  │  └─ Cross-platform → CHOOSE: flutter_secure_storage / react-native-keychain
│  │  │  │      ACTION: Wrapper over native secure storage
│  │  │  │
│  │  │  └─ NO: Simple app config/settings?
│  │  │     ├─ iOS → CHOOSE: UserDefaults (unencrypted)
│  │  │     │          ACTION: Simple, built-in, non-sensitive only
│  │  │     │
│  │  │     ├─ Android → CHOOSE: SharedPreferences or DataStore
│  │  │     │          ACTION: DataStore preferred (Jetpack Compose ready)
│  │  │     │
│  │  │     └─ Cross-platform → CHOOSE: AsyncStorage (React Native) / FlutterPrefs
│  │  │         ACTION: Simple key-value store
│  │  │
│  │  └─ NEXT: Use selected solution, minimal schema
│  │
│  ├─ MODERATE (relational data, multiple entities, queries):
│  │  │
│  │  ├─ Sync with server required?
│  │  │  │
│  │  │  ├─ YES: Real-time / offline-first critical?
│  │  │  │  │
│  │  │  │  ├─ YES: Complex sync logic (CRDT, conflict resolution)?
│  │  │  │  │  ├─ YES → CHOOSE: WatermelonDB (advanced ORM with sync)
│  │  │  │  │  │          ACTION: Lazy loading, sync protocol, local-first
│  │  │  │  │  │
│  │  │  │  │  └─ NO: Firebase Firestore acceptable?
│  │  │  │  │     ├─ YES → CHOOSE: Firestore offline mode
│  │  │  │  │     │          ACTION: enableOfflineSync, realtime updates
│  │  │  │  │     │
│  │  │  │  │     └─ NO → CHOOSE: Realm (with Realm Sync)
│  │  │  │  │         ACTION: Realm Sync (MongoDB backend) for real-time
│  │  │  │  │
│  │  │  │  └─ NO: Occasional sync (not critical offline):
│  │  │  │     └─ CHOOSE: SQLite/Room + REST polling
│  │  │  │         ACTION: Simple sync on app launch, background jobs
│  │  │  │
│  │  │  └─ NO: Local-only, no server sync:
│  │  │     │
│  │  │     ├─ Platform: iOS?
│  │  │     │  ├─ YES: iOS 17+ only?
│  │  │     │  │  ├─ YES → CHOOSE: SwiftData
│  │  │     │  │  │          ACTION: New Apple framework, async/await native
│  │  │     │  │  │
│  │  │     │  │  └─ NO: Support iOS 13+?
│  │  │     │  │     └─ CHOOSE: Core Data
│  │  │     │  │         ACTION: Mature, first-party, Xcode integration
│  │  │     │  │
│  │  │     │  └─ Platform: Android?
│  │  │     │     └─ CHOOSE: Room (Jetpack)
│  │  │     │         ACTION: SQLite abstraction, compile-time safety
│  │  │     │
│  │  │     ├─ Cross-platform (React Native / Flutter)?
│  │  │     │  │
│  │  │     │  ├─ Team knows SQL?
│  │  │     │  │  ├─ YES → CHOOSE: SQLite (react-native-sqlite-storage or sqflite)
│  │  │     │  │  │          ACTION: Direct SQL control, familiar syntax
│  │  │     │  │  │
│  │  │     │  │  └─ NO: Prefer ORM?
│  │  │     │  │     ├─ YES → CHOOSE: Realm (cross-platform)
│  │  │     │  │     │          ACTION: Object database, no SQL needed
│  │  │     │  │     │
│  │  │     │  │     └─ NO: High performance critical?
│  │  │     │  │        └─ CHOOSE: MMKV (key-value at scale)
│  │  │     │  │            ACTION: mmap'd file, very fast, <10GB data
│  │  │     │  │
│  │  │     │  └─ CHOOSE: Hive (Flutter-optimized object database)
│  │  │     │      ACTION: Type-safe, fast, Dart-native
│  │  │     │
│  │  │     └─ CHOOSE: SQLite (fallback, universal)
│  │  │         ACTION: Most compatible, manual migrations
│  │  │
│  │  └─ NEXT: Set up migrations, schema versioning
│  │
│  └─ COMPLEX (normalized relational + transactions + encryption):
│     │
│     ├─ Encryption required (HIPAA, GDPR)?
│     │  ├─ YES: Platform?
│     │  │  ├─ iOS → CHOOSE: Core Data + database encryption kit
│     │  │  │          ACTION: SQLCipher via Realm or Core Data
│     │  │  │
│     │  │  ├─ Android → CHOOSE: Room + SQLCipher
│     │  │  │          ACTION: Database-level encryption
│     │  │  │
│     │  │  └─ Cross-platform → CHOOSE: Realm with encryption (native)
│     │  │      ACTION: Built-in encryption, transparent access
│     │  │
│     │  └─ NO: Search requirements (full-text)?
│     │     ├─ YES: Firebase Cloud Firestore?
│     │     │  ├─ YES → CHOOSE: Firestore (cloud-first, indexing)
│     │     │  │          ACTION: Automated FTS, query builder
│     │     │  │
│     │     │  └─ NO: Local search?
│     │     │     └─ CHOOSE: SQLite FTS5 module
│     │     │         ACTION: Full-text search extension
│     │     │
│     │     └─ CHOOSE: Realm + Realm Query Language
│     │         ACTION: Powerful queries, flexible schema
│     │
│     └─ NEXT: Implement transaction management, schema versioning
│
└─ FINAL ACTION: Select and configure chosen storage solution
   Migration path from server to local, sync strategy, backup plan
```

---

## 6. Testing Strategy Selection Tree

Determine testing approach based on app type and risk profile.

```
START: Planning testing strategy?
│
├─ Project risk level?
│  │
│  ├─ HIGH (fintech, healthcare, mission-critical):
│  │  │
│  │  ├─ Testing pyramid ratio: E2E:Integration:Unit = 10:30:60
│  │  │  ACTION: Majority unit tests, integration with real services, few E2E critical paths
│  │  │
│  │  ├─ UNIT TESTS (60%):
│  │  │  ├─ What: Pure functions, viewmodels, repositories, utilities
│  │  │  ├─ Tool selection:
│  │  │  │  ├─ React Native → Jest + @testing-library/react-native
│  │  │  │  ├─ Flutter → test + mocktail packages
│  │  │  │  ├─ Swift → XCTest + SwiftTesting (iOS 17+)
│  │  │  │  └─ Kotlin → JUnit5 + mockk
│  │  │  └─ Coverage target: >80% for business logic, >60% overall
│  │  │
│  │  ├─ INTEGRATION TESTS (30%):
│  │  │  ├─ What: API calls (mocked), database operations, state flows
│  │  │  ├─ Tool selection:
│  │  │  │  ├─ React Native → Jest with mock modules
│  │  │  │  ├─ Flutter → integration_test package + mockito
│  │  │  │  ├─ Swift → XCTest with URLSession mocks
│  │  │  │  └─ Kotlin → MockWebServer + Testcontainers
│  │  │  └─ Use: testEnvironment API responses, offline scenarios
│  │  │
│  │  ├─ E2E TESTS (10%):
│  │  │  ├─ What: Critical user flows only (payment, auth, critical features)
│  │  │  ├─ Tool selection:
│  │  │  │  ├─ React Native → Detox (iOS/Android)
│  │  │  │  ├─ Flutter → Flutter Driver or integration_test
│  │  │  │  ├─ Native → XCUITest (iOS), Espresso (Android)
│  │  │  │  └─ PWA → Cypress or Playwright
│  │  │  └─ Use: Real device testing, visual regression for critical screens
│  │  │
│  │  ├─ ADDITIONAL TESTING:
│  │  │  ├─ Security: OWASP Mobile Top 10 scan, dependency audit
│  │  │  ├─ Performance: Lighthouse, APK analyzer, bundle size tracking
│  │  │  ├─ Accessibility: a11y testing suite per framework
│  │  │  └─ Compliance: HIPAA/GDPR audit for data handling
│  │  │
│  │  └─ CI/CD: Run all tests on every commit, E2E nightly
│  │
│  ├─ MEDIUM (social app, e-commerce, regular features):
│  │  │
│  │  ├─ Testing pyramid ratio: E2E:Integration:Unit = 10:20:70
│  │  │  ACTION: Balanced approach, unit-heavy, strategic integration/E2E
│  │  │
│  │  ├─ UNIT TESTS (70%):
│  │  │  ├─ What: All business logic, state management, helpers
│  │  │  ├─ Coverage: >70% for critical paths
│  │  │  └─ Tools: Framework standard + testing library
│  │  │
│  │  ├─ INTEGRATION TESTS (20%):
│  │  │  ├─ What: API integration (with mock server), key workflows
│  │  │  └─ Tools: Mock servers (MSW for web, HttpMock for native)
│  │  │
│  │  ├─ E2E TESTS (10%):
│  │  │  ├─ What: Main user journeys (signup → purchase, search → view)
│  │  │  └─ Tools: Detox (native), Cypress (web)
│  │  │
│  │  └─ CI/CD: Unit/integration on PR, E2E on release branch
│  │
│  └─ LOW (prototype, internal tool, MVP):
│     │
│     ├─ Testing pyramid ratio: E2E:Integration:Unit = 20:20:60
│     │  ACTION: Minimal testing, focus on coverage of critical paths
│     │
│     ├─ UNIT TESTS (60%):
│     │  ├─ What: Core business logic only
│     │  └─ Coverage: >50% acceptable
│     │
│     ├─ INTEGRATION TESTS (20%):
│     │  └─ What: API happy path, no error scenarios yet
│     │
│     ├─ E2E TESTS (20%):
│     │  ├─ What: Manual testing + one automated happy path
│     │  └─ Tools: Simple, fast (avoid heavy frameworks)
│     │
│     └─ CI/CD: Basic linting, compile check
│
├─ Test data strategy?
│  │
│  ├─ Fixtures: Pre-built test data, JSON files
│  ├─ Factories: Faker libraries, dynamic test data generation
│  ├─ Mocks: Service mocks, mock servers (Mock Server, MSW, http-mock)
│  └─ Real staging: Test against staging backend for integration tests
│
├─ Performance testing?
│  │
│  ├─ HIGH risk: Baseline metrics, CI monitoring (APK size, startup time)
│  ├─ MEDIUM risk: Periodic profiling, memory leak detection
│  └─ LOW risk: Manual spot-checks, no CI automation needed
│
└─ FINAL ACTION: Choose tools, set up CI/CD matrix per framework
   Create test data strategy, establish coverage thresholds
```

---

## 7. Backend/API Architecture Selection Tree

Choose API design pattern and backend architecture.

```
START: Designing backend API?
│
├─ Data fetch patterns?
│  │
│  ├─ Mostly READS (social feed, search results, catalog):
│  │  │
│  │  ├─ Real-time updates needed (live feed)?
│  │  │  ├─ YES: Heavy concurrent users (>10k)?
│  │  │  │  ├─ YES → CHOOSE: GraphQL with subscriptions or gRPC streaming
│  │  │  │  │          ACTION: Subscription service, connection pooling
│  │  │  │  │
│  │  │  │  └─ NO → CHOOSE: REST polling + Server-Sent Events (SSE)
│  │  │  │      ACTION: Polling interval 5-30s, SSE for high-frequency
│  │  │  │
│  │  │  └─ NO: Occasional refresh sufficient?
│  │  │     ├─ YES: Mobile first, bandwidth-critical?
│  │  │     │  ├─ YES → CHOOSE: GraphQL (query only what you need)
│  │  │     │  │          ACTION: Reduce payload, field-level optimization
│  │  │     │  │
│  │  │     │  └─ NO: Simplicity priority?
│  │  │     │     └─ CHOOSE: REST (simple, cacheable)
│  │  │     │         ACTION: HTTP caching headers, CDN friendly
│  │  │     │
│  │  │     └─ CHOOSE: gRPC (if internal services, not for mobile first)
│  │  │         ACTION: Protobuf, binary efficient
│  │  │
│  │  └─ NEXT: Implement read optimization (pagination, cursor-based)
│  │
│  ├─ Mostly WRITES (collaborative app, messaging, game):
│  │  │
│  │  ├─ Conflict resolution needed (two users edit same doc)?
│  │  │  ├─ YES: CRDT/OT required?
│  │  │  │  ├─ YES → CHOOSE: Custom WebSocket protocol or tRPC + Yjs
│  │  │  │  │          ACTION: Implement operational transform or CRDT
│  │  │  │  │
│  │  │  │  └─ NO: Last-write-wins acceptable?
│  │  │  │     └─ CHOOSE: GraphQL mutations with version checking
│  │  │  │         ACTION: Optimistic locking, conflict detection
│  │  │  │
│  │  │  └─ NO: Simple write operations (create, update)?
│  │  │     ├─ Idempotency critical (duplicate prevention)?
│  │  │     │  ├─ YES → CHOOSE: REST POST/PATCH with idempotency keys
│  │  │     │  │          ACTION: X-Idempotency-Key header
│  │  │     │  │
│  │  │     │  └─ NO: tRPC (type-safe) or REST
│  │  │     │     └─ CHOOSE: Based on team preference
│  │  │     │
│  │  │     └─ NEXT: Implement write validation, transaction handling
│  │
│  ├─ MIXED (social app: read feed, write posts/comments):
│  │  │
│  │  ├─ Type-safety across mobile + backend required?
│  │  │  ├─ YES: JavaScript/TypeScript backend?
│  │  │  │  ├─ YES → CHOOSE: tRPC (end-to-end type safety)
│  │  │  │  │          ACTION: Shared types, auto-generated clients
│  │  │  │  │
│  │  │  │  └─ NO → CHOOSE: OpenAPI with code generation
│  │  │  │      ACTION: Generate Dart/Swift/Kotlin clients
│  │  │  │
│  │  │  └─ NO: Flexible API contracts acceptable?
│  │  │     ├─ YES: Complex queries with filtering?
│  │  │     │  ├─ YES → CHOOSE: GraphQL
│  │  │     │  │          ACTION: Powerful query language, schema documentation
│  │  │     │  │
│  │  │     │  └─ NO → CHOOSE: REST
│  │  │     │      ACTION: Simple, familiar, cacheable
│  │  │     │
│  │  │     └─ NEXT: Implement caching strategy
│  │
│  └─ Legacy API required (no backend control)?
│     └─ CHOOSE: GraphQL federation or BFF (Backend for Frontend)
│         ACTION: Adapter layer, schema stitching
│
├─ Caching strategy?
│  │
│  ├─ HTTP caching headers?
│  │  ├─ YES: Set Cache-Control for GET endpoints (REST)
│  │  │          ACTION: max-age=300 for frequently read data
│  │  │
│  │  └─ NO: Need custom caching (GraphQL, gRPC)?
│  │     └─ Implement client-side cache (Apollo, TanStack Query)
│  │
│  ├─ Server-side cache?
│  │  ├─ HIGH traffic: Redis cache layer
│  │  ├─ MEDIUM: Database query result caching
│  │  └─ LOW: Direct database queries
│  │
│  └─ Stale-while-revalidate pattern?
│     └─ YES: Serve cached + refresh in background
│         ACTION: Better perceived performance
│
├─ Error handling & resilience?
│  │
│  ├─ HTTP status codes: Use standard (200, 400, 401, 404, 500)
│  ├─ Error response format: Consistent error objects (code, message, details)
│  ├─ Retry strategy: Exponential backoff with jitter
│  ├─ Circuit breaker: Fail fast if service unhealthy
│  └─ Rate limiting: Communicate limits in headers (X-RateLimit-*)
│
└─ FINAL ACTION: Document API specification (OpenAPI/Swagger or GraphQL schema)
   Set up API versioning strategy, monitor usage, plan for evolution
```

---

## 8. Deployment Strategy Selection Tree

Choose distribution and update strategy based on audience and requirements.

```
START: Planning app distribution?
│
├─ Distribution channel?
│  │
│  ├─ PUBLIC APP STORE (iOS App Store, Google Play):
│  │  │
│  │  ├─ Review time acceptable (1-3 days Apple, instant Google)?
│  │  │  ├─ YES: Over-the-air (OTA) updates needed?
│  │  │  │  │
│  │  │  │  ├─ YES: Minor updates only (non-critical)?
│  │  │  │  │  ├─ YES → CHOOSE: App Store + CodePush / EAS Updates
│  │  │  │  │  │          ACTION: Instant minor updates, App Store for major
│  │  │  │  │  │
│  │  │  │  │  └─ NO: All updates via store?
│  │  │  │  │     └─ CHOOSE: Standard App Store release cycle
│  │  │  │  │         ACTION: Plan reviews, release notes, staged rollout
│  │  │  │  │
│  │  │  │  └─ NO: OTA updates critical (hotfixes)?
│  │  │  │     └─ CHOOSE: App Store + internal/TestFlight for testing, custom update check
│  │  │  │         ACTION: In-app update prompts (built-in API)
│  │  │  │
│  │  │  └─ NO: Fastest possible iteration (no review delay)?
│  │  │     ├─ YES: Can delay public release by weeks?
│  │  │     │  ├─ YES → CHOOSE: Open Beta (Google Play beta, TestFlight)
│  │  │     │  │          ACTION: Beta testing period before public
│  │  │     │  │
│  │  │     │  └─ NO: Need immediate public availability?
│  │  │     │     └─ CHOOSE: PWA instead of native app
│  │  │     │         ACTION: No review process, instant updates
│  │  │     │
│  │  │     └─ CHOOSE: Parallel release: beta + stable
│  │  │         ACTION: TestFlight for early users, App Store for GA
│  │  │
│  │  └─ NEXT: Set up CI/CD for app signing, release pipeline
│  │
│  ├─ ENTERPRISE / INTERNAL DISTRIBUTION:
│  │  │
│  │  ├─ iOS only:
│  │  │  ├─ In-house MDM (Mobile Device Management)?
│  │  │  │  ├─ YES → CHOOSE: Enterprise distribution (in-house signing)
│  │  │  │  │          ACTION: ipa signed with enterprise certificate
│  │  │  │  │
│  │  │  │  └─ NO: Ad-hoc distribution?
│  │  │  │     └─ CHOOSE: Ad-hoc provisioning (limited devices)
│  │  │  │         ACTION: UDID-registered devices only
│  │  │  │
│  │  │  └─ NEXT: Use TestFlight for widest testing (up to 10k users)
│  │  │
│  │  ├─ Android + iOS:
│  │  │  │
│  │  │  ├─ Need OTA updates for enterprise apps?
│  │  │  │  ├─ YES → CHOOSE: Custom enterprise distribution + app wrapper
│  │  │  │  │          ACTION: Self-hosted APK/IPA, auto-update check
│  │  │  │  │
│  │  │  │  └─ NO: Manual distribution acceptable?
│  │  │  │     └─ CHOOSE: Email distribution, shared folder, or internal CDN
│  │  │  │         ACTION: Simplest for small teams
│  │  │  │
│  │  │  └─ NEXT: Plan update notification, in-app prompts
│  │  │
│  │  └─ CHOOSE: Internal app store (MDM + app portal)
│  │      ACTION: Samsung Knox, Microsoft Intune, or custom portal
│  │
│  └─ BETA / TESTING DISTRIBUTION:
│     │
│     ├─ iOS:
│     │  ├─ Small internal team (<10): Ad-hoc provisioning
│     │  ├─ Extended beta (10-10k): TestFlight
│     │  └─ Public beta: TestFlight + marketing
│     │
│     ├─ Android:
│     │  ├─ Internal: Direct APK distribution, Firebase App Tester
│     │  ├─ Extended: Google Play internal/closed/open testing tracks
│     │  └─ Public: Google Play open beta track
│     │
│     └─ Cross-platform:
│        ├─ Firebase App Distribution (easiest for native)
│        └─ BrowserStack / Appetize for web distribution
│
├─ Staged rollout strategy?
│  │
│  ├─ CRITICAL APP (fintech, healthcare):
│  │  │
│  │  ├─ Rollout stages: 1% → 5% → 25% → 100%
│  │  ├─ Monitor: Crash rate, ANR rate, negative reviews
│  │  ├─ Rollback plan: Can revert if issues detected
│  │  └─ Duration: 3-7 days per stage
│  │
│  ├─ STANDARD APP:
│  │  │
│  │  ├─ Rollout stages: 5% → 50% → 100%
│  │  ├─ Monitor: Error reports, analytics
│  │  └─ Duration: 1-3 days per stage
│  │
│  └─ LOW-RISK UPDATES:
│     └─ Full rollout immediately
│
├─ Version management?
│  │
│  ├─ Semantic versioning: MAJOR.MINOR.PATCH (1.2.3)
│  ├─ Build number: Auto-increment per release (100, 101, 102...)
│  ├─ Deprecation: Support N-1 versions, deprecate older
│  └─ Minimum version enforcement: Block out-of-date app with warning
│
└─ FINAL ACTION: Set up app signing certificates, CI/CD release pipeline
   Automate TestFlight/beta uploads, configure staged rollout, plan monitoring
```

---

## Decision Tree Usage Guide

**How to traverse these trees:**

1. Start at the top (START:) of the relevant tree
2. Answer each question YES or NO
3. Follow the arrow (├──) to the next decision
4. When you reach CHOOSE or ACTION, that's your recommendation
5. If tree says NEXT, proceed to the specified subtree

**Example traversal (Framework Selection):**
- "Need multi-platform (iOS + Android)?" → YES
- "Team JavaScript/TypeScript proficient?" → YES
- "Can afford Expo managed services?" → NO
- "Need native modules?" → YES
- Result: **React Native (Bare) with native modules**

**Tips:**
- All decisions are actionable—each endpoint includes implementation steps
- Cross-reference trees when decisions depend on other choices (e.g., state management depends on framework choice)
- Update these trees quarterly as technology evolves
- Use trees in team discussions to build consensus on architecture
