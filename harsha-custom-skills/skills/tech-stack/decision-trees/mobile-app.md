# Decision Tree: Mobile Application

## Entry Point

```
What kind of mobile app?
├── Simple app (info, forms, basic CRUD)
│   → Evaluate PWA first (cheapest, fastest)
├── Cross-platform (iOS + Android from one codebase)
│   → CROSS-PLATFORM PATH
├── Native (maximum performance, deep OS integration)
│   → NATIVE PATH
├── Existing web app → mobile presence
│   → WRAPPER PATH
└── Real-time collaborative (like Google Docs, Figma)
    → OFFLINE-FIRST PATH
```

---

## DECISION MATRIX: Native vs Cross-Platform vs PWA

Choosing the right approach is critical. The wrong choice costs months of rework.

| Factor | PWA | Cross-Platform (Expo/Flutter) | Native (Swift/Kotlin) |
|--------|-----|-------------------------------|----------------------|
| **Time to MVP** | 2–3 weeks | 3–4 weeks | 4–6 weeks |
| **Team Size** | 1–2 devs (web devs) | 1–2 devs (JS or Dart) | 2–4 devs (native devs) |
| **Performance** | Good (60fps) | Good (90% native) | Excellent (near-native) |
| **App Store** | No store listing | Both stores required | Both stores required |
| **iOS Limitations** | Significant (no push, offline, widgets) | Minor (near-native) | None |
| **Offline** | Partial (service worker) | Yes (built-in) | Yes (built-in) |
| **Push Notifications** | Android only | Both | Both |
| **Bluetooth/NFC** | No | Limited (Expo) | Full support |
| **Hardware Access** | Limited (camera, GPS) | Good | Full |
| **Cost @ 100k users** | $0–20/mo | $50–300/mo | $100–500/mo |
| **When to Use** | Info apps, internal tools | 80% of use cases | Games, AR, real-time heavy |

### Quick Decision Tree

```
Does the app need to work offline?
├─ YES → Native or Cross-platform required
└─ NO → Continue...

Does it need to be on iOS AND Android?
├─ NO (iOS only or Android only) → Native (Swift or Kotlin)
├─ YES → Continue...

Team experienced in React/TypeScript?
├─ YES → Use Expo (React Native)
├─ NO → Use Flutter or native

Tight launch deadline (<4 weeks)?
├─ YES → Expo or PWA
└─ NO → Native (Swift/Kotlin)

Is this a PWA-suitable use case?
(Info app, internal tool, doesn't need offline, push not critical)
├─ YES → PWA (cheapest, no app store headache)
└─ NO → Cross-platform or native
```

---

## PWA FIRST (When Native App Isn't Needed)

PWA (Progressive Web App) is the dark horse. It's fast, cheap, and works for many use cases.

### When PWA is Sufficient

- Information apps (news, documentation, portfolio)
- Internal business tools (for employees)
- Basic forms + data entry
- Light productivity apps (note-taking, task lists)
- Anything that doesn't need Bluetooth/NFC/native widgets

### PWA Capabilities in 2025–2026

| Feature | iOS | Android | Status |
|---------|-----|---------|--------|
| Home screen install | Yes | Yes | Full |
| Offline mode (service workers) | Yes | Yes | Full |
| Push notifications | Limited (no persistent) | Yes | Partial on iOS |
| Camera/GPS access | Yes | Yes | Full |
| File system | Limited | Yes | Partial |
| Biometrics | Touch ID only | Full | Partial |
| Bluetooth/NFC | No | No | Not available |
| Background sync | No | Yes | Partial |
| App widgets | No | No | Not available |

**iOS Reality Check:** PWA on iOS works but lacks critical features. Consider native if iOS is priority.

### PWA Stack ($0–20/mo)

| Component | Choice | Cost | Notes |
|-----------|--------|------|-------|
| Framework | Next.js or SvelteKit | $0 | Both zero-cost |
| PWA Toolkit | next-pwa or vite-pwa | $0 | Handles service workers, manifest |
| Styling | Tailwind + shadcn/ui | $0 | Mobile-first design |
| Database | Supabase Free | $0 | Or use IndexedDB for local-only |
| Hosting | Cloudflare Pages or Vercel Free | $0 | Static hosting |
| Analytics | PostHog or Umami | $0–15 | Track installs, usage |
| Push (optional) | Firebase Cloud Messaging | $0 | Only works on Android |
| **Total** | | **$0–20/mo** | |

**Example PWA Stack: Mobile-friendly expense tracker**
```yaml
Frontend: Next.js + App Router + shadcn/ui
PWA: next-pwa with offline service worker
Local State: IndexedDB (built-in browser storage)
Sync: When back online, sync to Supabase
Database: Supabase (for sync, backup, sharing)
Push Notifications: Firebase Cloud Messaging (Android only)
Hosting: Vercel Free or Cloudflare Pages
```

**Launch:** 2 weeks for one developer.

### PWA Gotchas

1. **iOS push notifications don't work** — Use email fallback, SMS, or web notifications
2. **PWA needs HTTPS everywhere** — Cloudflare Pages includes it; Vercel does too
3. **Manifest updates require rebuild** — Change the manifest.json version on deploy
4. **IndexedDB is limited** — ~50MB per origin (varies by browser). Good for local data, sync to server.

---

## CROSS-PLATFORM PATH

Cross-platform (one codebase, both platforms) is the sweet spot for most apps.

### React Native vs Flutter: Detailed Comparison

| Factor | React Native (Expo) | Flutter |
|--------|---------------------|---------|
| **Language** | TypeScript/JavaScript | Dart |
| **Learning Curve** | Low (if web dev background) | Medium (Dart is new) |
| **Performance** | 90% native speed | 98% native speed (better) |
| **UI Library** | React Native Built-in + expo-ui | Flutter built-in + many 3rd party |
| **Hot Reload** | Yes (instant) | Yes (instant) |
| **OTA Updates** | EAS Update (built-in, $99/mo) | Manual or CodeMagic (different cost) |
| **Community** | Larger (React ecosystem) | Growing (but smaller) |
| **Jobs/Hirability** | More job postings | Fewer but growing |
| **Build Complexity** | EAS handles it (simpler) | Codemagic handles it (same) |
| **App Size** | 40–80MB (larger) | 20–40MB (smaller) |
| **Bundle Updates** | Over-the-air (EAS) | Harder to update |
| **Firebase Integration** | Good | Excellent |
| **Third-party Libraries** | Fewer (web dev focused) | More (mobile dev focused) |
| **Best For** | Teams with React background | Green-field projects, performance critical |

**General Rule:** Use Expo if you know React. Use Flutter if you want slightly better performance or are starting from scratch.

### Expo (React Native) Ecosystem

Expo is a batteries-included React Native platform. You don't manage native code (mostly).

#### Expo Stack by Scale

**MVP (First Launch)**

| Component | Choice | Cost | Notes |
|-----------|--------|------|-------|
| Framework | Expo (React Native) | $0 | No native code, no Xcode/Android Studio |
| TypeScript | Included | $0 | Expo supports TS out of box |
| UI Library | Expo UI or React Native Paper | $0 | Built-in components |
| Icons | Expo Vector Icons | $0 | 10k+ icons included |
| Database | Supabase Free | $0 | Postgres + Auth + Storage |
| Auth | Supabase Auth | $0 | Email, Google, GitHub, etc. |
| Storage | Supabase Storage | $0 | 1GB free |
| State Management | Zustand | $0 | Simple, lightweight |
| API Calls | React Query + Axios | $0 | Handles caching, offline |
| Build/CI | EAS Build Free (30/mo) | $0 | Cloud builds, no Mac needed |
| Push Notifications | Expo Notifications | $0 | Free with Expo |
| App Store | Developer account | $99/year (iOS), $25 (Android) | Required |
| **Total** | | **$0/mo** | (+$99/year Apple Dev) |

**Launch:** 3–4 weeks, 1–2 developers.

**Example MVP: Chat app**
```yaml
Framework: Expo (React Native)
UI: Expo UI components + Tailwind-like styling
State: Zustand (app state) + React Query (API)
Database: Supabase (messages, users, auth)
Real-time: Supabase Realtime (WebSocket)
Push Notifications: Expo Notifications via Firebase
Backend: None (Supabase is your backend)
Hosting: EAS Build handles compile
App Stores: iOS App Store + Google Play Store
```

**Growing (5k–50k users)**

| Component | Choice | Cost | Notes |
|-----------|--------|------|-------|
| Framework | Expo (still) | $0 | Can stay on Expo for most cases |
| Database | Supabase Pro ($25) or Neon ($19) | $19–25 | Better reliability, backups |
| Auth | Clerk ($0–25/mo) | $0 | Better UX than Supabase Auth |
| Push Notifications | Firebase Cloud Messaging | $0 | Cheaper, more reliable than Expo |
| Monitoring | Sentry ($0–29/mo) | $0 | Error tracking |
| CI/CD | EAS Build Pro ($99/mo) | $99 | Unlimited builds (vs 30/mo free) |
| Storage | Cloudflare R2 | $5–20 | Cheaper than Supabase for large files |
| Analytics | PostHog or Amplitude | $0–100 | Product analytics |
| **Total** | | **$150–250/mo** | |

**Example Growing: Social network app**
```yaml
Framework: Expo
UI: Expo UI + shadcn/ui-inspired components
Database: Supabase Pro (more reliability)
Real-time: Supabase Realtime + custom WebSocket
Push: Firebase Cloud Messaging (cheaper at scale)
Auth: Clerk (better team/social features)
Storage: Cloudflare R2 (user uploads, profile photos)
Analytics: PostHog (user behavior tracking)
CI/CD: EAS Build Pro (unlimited builds)
Monitoring: Sentry (error tracking)
```

**Scaling (50k+ users)**

| Component | Choice | Cost | Notes |
|-----------|--------|------|-------|
| Framework | Expo (but might use custom Expo modules) | $0 | Some native code exposure |
| API Layer | Custom (Hono/Fastify) | $50 | Own the backend for control |
| Database | Neon Scale ($69) or AWS RDS | $69–200 | Separate from other services |
| Auth | WorkOS ($0–free to 1M) or Auth0 | $0–100 | Enterprise auth, SSO |
| Push Notifications | Firebase Cloud Messaging | $0 | Still free, just more volume |
| Monitoring | Sentry ($30+) + DataDog ($100+) | $130+ | Comprehensive observability |
| CI/CD | EAS Build Pro ($99) | $99 | Still using Expo |
| Caching | Redis (Upstash Pro) | $20–50 | Query caching |
| Analytics | Amplitude ($995+) or internal | $0–1000 | Detailed analytics |
| **Total** | | **$400–600/mo** | |

**Real Scaling Example: Fintech app (Stripe-like dashboard)**
```yaml
Framework: Expo (with custom native modules for biometrics)
UI: Expo UI + shadcn-inspired design system
API: FastAPI or Node.js (separate from Expo)
Database: PostgreSQL on Neon Scale
Real-time: Socket.io (self-hosted or Socket.io platform)
Auth: WorkOS (SSO, enterprise users)
Push: Firebase Cloud Messaging
Storage: Cloudflare R2
Payments: Stripe API (from backend)
Analytics: Amplitude
Monitoring: Sentry + DataDog
CI/CD: EAS Build Pro
```

### Flutter Stack

Flutter is Google's mobile framework. Faster than React Native, smaller apps, but less job market.

#### Flutter by Scale

**MVP**

| Component | Choice | Cost | Notes |
|-----------|--------|------|-------|
| Framework | Flutter 3.x | $0 | Free, open-source |
| Language | Dart | $0 | Learning curve if new to Dart |
| UI Library | Material 3 or Cupertino | $0 | Built-in, Google-designed |
| Database | Firebase Firestore | $0 | Free tier covers MVP |
| Auth | Firebase Auth | $0 | Included with Firebase |
| Storage | Firebase Cloud Storage | $0 | 5GB free |
| State Management | Riverpod or Provider | $0 | Lightweight |
| API | Http package or Dio | $0 | Built-in Dart libraries |
| Build/CI | Codemagic Free | $0 | Cloud builds, includes iOS |
| Push Notifications | Firebase Cloud Messaging | $0 | Built into Firebase |
| App Store | Developer accounts | $99/year (iOS), $25 (Android) | Required |
| **Total** | | **$0/mo** | (+$99/year Apple Dev) |

**Launch:** 3–4 weeks, 1–2 developers (if Dart experience exists).

**Example MVP: Todo app**
```yaml
Framework: Flutter
UI: Material 3 (Google's design system)
State: Riverpod (reactive state management)
Database: Firebase Firestore
Auth: Firebase Auth
Storage: Firebase Cloud Storage
Real-time: Firestore's built-in sync
Push: Firebase Cloud Messaging
Backend: Firestore handles it all (serverless)
```

**Growing (Firebase → Custom API)**

| Component | Choice | Cost | Notes |
|-----------|--------|------|-------|
| Framework | Flutter | $0 | Same |
| Database | Supabase or custom PostgreSQL | $25–50 | More control than Firebase |
| API | Dart backend (Shelf or Dart Frog) | $0 | Write backend in Dart too |
| CI/CD | Codemagic ($75/mo) | $75 | More than free tier |
| Analytics | Firebase Analytics + custom | $0–50 | Firebase free, custom $$$ |
| Monitoring | Sentry ($0–29/mo) | $0 | Error tracking |
| **Total** | | **$100–175/mo** | |

**Scaling**

| Component | Choice | Cost | Notes |
|-----------|--------|------|-------|
| Framework | Flutter | $0 | Same |
| API | Go or Rust backend | $50 | Better performance than Dart |
| Database | PostgreSQL cluster | $100–300 | High availability |
| Auth | Keycloak or custom | $0–100 | Full control |
| CI/CD | Codemagic ($200/mo) | $200 | Top tier |
| Monitoring | DataDog + Sentry | $150+ | Comprehensive |
| Analytics | Custom (event tracking) | $0–100 | Internal analytics |
| **Total** | | **$300–500/mo** | |

### Cross-Platform: Common Mistakes

1. **Choosing Expo when native code is needed early** — Expo doesn't allow native modules initially. Plan for this.
2. **Not budgeting for EAS Build ($99/mo)** — Free tier has 30 builds/month. Most teams exceed this.
3. **Firebase lock-in** — Firebase is cheap early, expensive at scale. Plan to migrate to custom API.
4. **Ignoring platform differences** — iOS and Android have different UX patterns. Design for both.
5. **Over-optimizing before launch** — Ship first, optimize at 10k users.

---

## NATIVE PATH

Native development: You write separate iOS (Swift) and Android (Kotlin) codebases.

### When Native is Better

Go native if:
- Heavy animations (60fps required throughout) or AR/VR
- Complex gestures (pinch, rotate, swipe combinations)
- Bluetooth/NFC/smart home integration
- Battery-critical background processing (location tracking)
- Apple/Google widgets
- App size <10MB requirement
- Extreme performance needed (heavy computing)

Otherwise, cross-platform is simpler.

### iOS (Swift + SwiftUI)

**Tech Stack**

| Component | Choice | Notes |
|-----------|--------|-------|
| Language | Swift 5.9+ | Modern, type-safe |
| UI Framework | SwiftUI (iOS 16+) | Reactive, easier than UIKit |
| Architecture | MVVM or TCA | MVVM simpler, TCA for complex state |
| Networking | URLSession + async/await | Built-in, no 3rd party needed |
| Local Storage | SwiftData (iOS 17+) or Core Data | SwiftData is newer, simpler |
| State Management | SwiftUI @State/@EnvironmentObject | Built-in, no Redux-like libraries |
| Backend | Supabase or custom API | Same as cross-platform |
| CI/CD | Xcode Cloud ($25/mo) or GitHub Actions + Fastlane | Xcode Cloud is Apple's official |

**iOS Stack by Scale**

**MVP**
```yaml
Framework: SwiftUI
Architecture: MVVM
Database: Firebase or Supabase
Auth: Firebase Auth or Supabase Auth
Storage: Firebase Cloud Storage or Supabase Storage
API: URLSession with Decodable
Networking: Custom API client wrapper
CI/CD: GitHub Actions + Fastlane (free)
Cost: $0 + $99/year Apple Developer
```

**Growing**
```yaml
Framework: SwiftUI
Architecture: MVVM with dependency injection
Database: Supabase Pro ($25)
Auth: Supabase Auth
Storage: Cloudflare R2 (cheaper images)
API: Custom backend API
Monitoring: Sentry ($0–29/mo)
Analytics: Firebase Analytics (free)
CI/CD: Xcode Cloud ($25/mo) or GitHub Actions
Cost: $25–29/mo + $99/year Apple Developer
```

**Scaling**
```yaml
Framework: SwiftUI + Widget Kit (for home screen widgets)
Architecture: MVVM + TCA for complex state
Database: PostgreSQL on custom backend
Auth: Custom or WorkOS
Storage: Cloudflare R2
API: Custom backend (Node/Python/Go)
Monitoring: Sentry ($30+) + DataDog
Analytics: Amplitude
CI/CD: Xcode Cloud ($25/mo)
Cost: $100–300/mo + $99/year Apple Developer
```

### Android (Kotlin + Jetpack Compose)

**Tech Stack**

| Component | Choice | Notes |
|-----------|--------|-------|
| Language | Kotlin | Java-compatible, modern, null-safe |
| UI Framework | Jetpack Compose (new) | Declarative, like SwiftUI |
| Architecture | MVVM + Hilt (dependency injection) | Industry standard |
| Networking | Retrofit + OkHttp | Popular, mature libraries |
| Local Storage | Room (SQLite wrapper) | Type-safe, integrates with Kotlin |
| State Management | ViewModel (Architecture Components) | Built-in, no 3rd party |
| Backend | Supabase or custom API | Same as iOS |
| CI/CD | GitHub Actions or Codemagic | Both free tier available |

**Android Stack by Scale**

**MVP**
```yaml
Framework: Jetpack Compose
Architecture: MVVM with ViewModel
Database: Firebase or Supabase
Auth: Firebase Auth or Supabase Auth
Storage: Firebase Cloud Storage
API: Retrofit + OkHttp
State: ViewModel (built-in)
CI/CD: GitHub Actions (free)
Cost: $0 + $25 one-time Google Play
```

**Growing**
```yaml
Framework: Jetpack Compose
Architecture: MVVM + Hilt (dependency injection)
Database: Supabase Pro ($25)
Auth: Supabase Auth
Storage: Cloudflare R2
API: Custom backend
Networking: Retrofit with interceptors
Monitoring: Sentry ($0–29/mo)
Analytics: Firebase Analytics
CI/CD: Codemagic ($75/mo) or GitHub Actions
Cost: $25–75/mo + $25 one-time Google Play
```

**Scaling**
```yaml
Framework: Jetpack Compose + Widgets (home screen)
Architecture: MVVM + Clean Architecture
Database: PostgreSQL on custom backend
Auth: Custom or WorkOS
Storage: Cloudflare R2
API: Custom backend (same as iOS)
Monitoring: Sentry ($30+) + DataDog
Analytics: Amplitude
CI/CD: Codemagic ($200/mo)
Cost: $200–400/mo + $25 Google Play
```

### Two Native Codebases (iOS + Android)

This is the **most expensive** approach: hire separate iOS and Android teams.

| Metric | Cost | Timeline |
|--------|------|----------|
| Team Size | 2 devs (1 iOS, 1 Android) | Start |
| Development Time | 4–6 weeks | MVP |
| Monthly Infra Cost | $100–300 | Same backend for both |
| Developer Cost | $300–500k/year | Median US salary, senior |
| When Worth It | 100k+ users, critical UX | After cross-platform MVPs |

**Decision:** Only go this route if:
1. You have 100k+ users (justifies the cost)
2. You have platform-specific UX requirements
3. You have funding to hire 2 senior developers

For most companies, Expo or Flutter gets you 80% of the way there at 20% of the cost.

---

## WRAPPER PATH (Existing Web App → Mobile)

You have a web app. You want it on iOS/Android without rewriting.

### Capacitor (Recommended)

Capacitor wraps your web app in a native WebView and exposes native APIs.

```yaml
Language: JavaScript/TypeScript (same as web)
Framework: React/Vue/Svelte (your existing web stack)
Native APIs: Camera, GPS, File system, Biometrics, Push, etc.
Performance: Good for most apps, not for games or heavy animation
Setup: Add @capacitor/core + native plugins
Deployment: Xcode for iOS, Android Studio for Android
Cost: $0 (open source) + app store fees
```

**Capacitor Stack**

| Component | Cost | Notes |
|-----------|------|-------|
| Capacitor Core | $0 | Open source |
| iOS Plugins | $0 | Camera, GPS, etc. |
| Android Plugins | $0 | Same |
| Push Notifications | $0 | With Firebase |
| Deep Linking | $0 | Included |
| Storage | $0 | Secure file storage |
| Hosting (web) | $0–20 | Same as your web app |
| **Total** | **$0** | Just plugin time |

**Example: Convert React web app to mobile with Capacitor**

```yaml
Web App: React + Next.js (existing)
Capacitor: Add @capacitor/core
Native APIs: @capacitor/camera, @capacitor/geolocation
Push: Firebase Cloud Messaging (free)
Build iOS: Xcode (opens Capacitor-generated project)
Build Android: Android Studio (opens Capacitor-generated project)
CI/CD: GitHub Actions + Fastlane (for iOS) + Gradle (for Android)
Cost: $0 (just plugin development time)
```

**Timeline:** 2–3 weeks to add Capacitor + native features.

### When Capacitor is NOT Enough

Capacitor works great until you need:
- 60fps animations throughout the app
- Complex gestures (multi-touch, pinch-rotate-drag)
- Background audio or location tracking
- Bluetooth/NFC integration
- Heavy computation
- Offline-first with full sync

If you need these → Use Expo or native.

### Cordova (Legacy)

Apache Cordova is the predecessor to Capacitor. It's older, less maintained.

Use Capacitor instead (it's a spiritual successor but much better).

---

## OFFLINE-FIRST & SYNC ARCHITECTURE

For real-time collaborative apps or apps that must work offline.

### Offline-First Technologies

| Technology | Type | Use Case | Cost |
|------------|------|----------|------|
| **WatermelonDB** | SQLite wrapper | Local-first CRUD | Free |
| **Turso** | Embedded SQLite + sync | Mobile + server sync | Free–$99/mo |
| **PowerSync** | Postgres ↔ local sync | Real-time collaboration | $50–500/mo |
| **Convex** | Cloud backend + real-time | Reactive data (Google Docs-like) | Free–$200/mo |
| **Evolu** | SQLite + Postgres + CRDT | Encryption, local-first | Free (open source) |

### Offline-First Stack for Collaborative Apps

**React Native + Convex (Easiest for real-time)**

```yaml
Framework: Expo (React Native)
Backend: Convex (replaces traditional API + database)
Real-time: Convex built-in (optimistic updates)
Offline: Works offline, syncs when back online
Auth: Convex Auth or Clerk
Cost: Free to $200/mo (Convex scales with usage)
Timeline: 2–3 weeks (Convex handles a lot)
```

**Web + Turso + PowerSync (Maximum control)**

```yaml
Frontend: React or Next.js
Database: PostgreSQL (remote)
Local Cache: SQLite (Turso embedded)
Sync Layer: PowerSync (syncs between local SQLite + Postgres)
Offline: Full offline, syncs when back
Auth: Custom
Cost: $50–500/mo (PowerSync)
Timeline: 3–4 weeks (more complex setup)
```

---

## BACKEND FOR MOBILE APPS

Mobile apps need a backend. Choose wisely: this decision affects your entire architecture.

### Backend Decision Matrix

| Backend | Setup Time | Scaling | Cost | When to Use |
|---------|-----------|---------|------|-----------|
| **Firebase** | 1 day | Unlimited | Free–$1000/mo | First-time mobile builders, rapid prototyping |
| **Supabase** | 1 day | 10k–50k users | Free–$100/mo | Web-first teams, Postgres preference |
| **Custom API** | 3–5 days | Any | $50–500/mo | Complex logic, control needed |
| **Convex** | 1 day | Unlimited | Free–$200/mo | Real-time/collaborative, sync |
| **Parse** | 2–3 days | Limited | Free (self-hosted) | DIY, wants control |

### Firebase (Google's Platform)

**Best for:** Mobile-first apps, real-time features, rapid prototyping.

**Pros:**
- Firestore: Real-time database, auto-sync
- Firebase Auth: Social login, phone auth, email verification
- Cloud Storage: File uploads, images
- Cloud Functions: Serverless backend
- FCM: Push notifications (free)
- Analytics: Built-in event tracking
- Remote Config: Feature flags

**Cons:**
- Data structure locks you into Firestore (hard to migrate)
- Pricing scales unpredictably (can spike)
- Limited query capabilities (no complex JOINs)
- Vendor lock-in

**Pricing:**
- Free tier: 1GB storage, 50k reads/day, 20k writes/day (enough for MVP)
- Growth: Pay per read/write/storage ($0.06 per 100k reads)
- Scale: Can get expensive (100k reads/day = $60/mo)

**Firebase Stack for Mobile:**

| Scale | Database | Auth | Storage | Functions | Cost |
|-------|----------|------|---------|-----------|------|
| **MVP** | Firestore Free | Firebase Auth | 5GB | 125k invocations/mo | $0 |
| **Growing** | Firestore Pay-as-you-go | Firebase Auth | Same | Increased quota | $50–200/mo |
| **Scaling** | Firestore paid | Firebase Auth | Same | Heavy usage | $500+/mo |

### Supabase (Open-source Firebase Alternative)

**Best for:** PostgreSQL-first teams, web-first developers, better pricing at scale.

**Pros:**
- PostgreSQL: Full query power, standard SQL
- Realtime: WebSocket subscriptions (like Firestore)
- Auth: Supabase Auth or external (Clerk, Auth0)
- Storage: File uploads, same as Firebase
- Open source: Can self-host (Render, Railway ~$7/mo)

**Cons:**
- PostgreSQL more complex than Firestore for simple apps
- Less mobile-specific features
- Realtime subscriptions can be slower than Firestore at scale

**Pricing:**
- Free: 500MB storage, 50k MAU, 2GB bandwidth (very generous)
- Pro: $25/mo (100GB storage, unlimited users)
- Scale: $100+/mo for large databases

**Supabase Stack:**

| Scale | Database | Auth | Storage | Realtime | Cost |
|-------|----------|------|---------|----------|------|
| **MVP** | Free (500MB) | Free | 1GB | Free | $0 |
| **Growing** | Pro ($25) | Same | More | Free | $25/mo |
| **Scaling** | Pro + Neon PostgreSQL | Clerk ($25) | R2 ($10) | Same | $60+/mo |

### Custom Backend

When Firebase/Supabase isn't enough: complex business logic, custom workflows, strict control.

**Tech Stacks:**

**Node.js Backend (TypeScript)**
```yaml
API: Hono, Fastify, or Express
Database: PostgreSQL on Neon or Supabase Pro
ORM: Drizzle or TypeORM
Auth: Clerk or Auth0
Hosting: Railway or Render ($7–20/mo)
Total: $25–50/mo
```

**Python Backend**
```yaml
API: FastAPI (async, modern)
Database: PostgreSQL
Auth: Auth0 or FastAPI + JWT
Hosting: Railway or Render
Cost: $25–50/mo
```

**Go Backend (Performance)**
```yaml
API: Gin or Echo
Database: PostgreSQL
Auth: Standard JWT
Hosting: Railway or Render
Cost: $25–50/mo
```

---

## PUSH NOTIFICATIONS

Every mobile app needs push notifications. Choose carefully: this affects your app store rating.

### Push Notification Services

| Service | iOS | Android | Cost | Best For |
|---------|-----|---------|------|----------|
| **Firebase Cloud Messaging** | Yes | Yes | Free | Any app (industry standard) |
| **OneSignal** | Yes | Yes | Free–$9/mo | Multi-channel (push, email, SMS) |
| **Expo Notifications** | Limited | Yes | Free (Expo) | Expo-only projects |
| **Apple APNs + FCM** | Yes | Yes | Free | Direct setup (more work) |
| **Pusher** | Yes | Yes | $5–100/mo | High-volume apps |
| **Ably** | Yes | Yes | $0–1000/mo | Real-time messaging, complex |

**Recommendation:** Firebase Cloud Messaging (free, works with any backend, industry standard).

### Implementing Push Notifications

**Expo + Firebase**
```yaml
1. Set up Firebase project (free)
2. Install expo-notifications + firebase-admin in backend
3. Get FCM server key, store in backend
4. Send push from backend to users
Cost: $0 (free Firebase tier)
```

**React Native + Firebase**
```yaml
1. Same as above
2. Set up iOS + Android push certificates (more work)
3. Configure Firebase credentials
Cost: $0 (Firebase) + $99/year Apple Developer
```

**Custom Backend + FCM**
```yaml
1. Generate FCM server key
2. Store user FCM tokens in your database
3. Send POST to FCM API from your backend
4. FCM routes message to iOS/Android
Cost: $0 (Firebase FCM is free)
```

---

## APP STORE COSTS & REQUIREMENTS

Publishing is expensive and requires accounts with both Apple and Google.

### App Store Economics

| Item | iOS | Android | Notes |
|------|-----|---------|-------|
| Developer Account | $99/year | $25 one-time | Required for app distribution |
| App Review Time | 1–3 days | Hours–1 day | iOS is stricter, slower |
| Rejection Rate | ~20% (first review) | ~5% | iOS rejects more frequently |
| Commission (In-app purchases) | 30% (15% if <$1M revenue) | 30% (15% if <$1M revenue) | You keep 70% of revenue |
| OTA Updates | Allowed (JavaScript changes) | Allowed | Can update without app review |
| App Clips (iOS) | $0 | N/A | Lite version, no install |
| Widgets | Yes (Widgets) | Yes (App Widgets) | Platform-specific |

### First-App Checklist

```
iOS:
✓ Enroll in Apple Developer Program ($99/year)
✓ Create App ID in App Store Connect
✓ Generate provisioning profiles + certificates (Xcode handles this)
✓ Create bundle identifier (com.yourcompany.appname)
✓ Build signed archive
✓ Upload via App Store Connect
✓ Fill out metadata (screenshots, description, keywords)
✓ Submit for review (1–3 days wait)

Android:
✓ Enroll in Google Play Console ($25 one-time)
✓ Create signed APK/AAB
✓ Upload to Google Play Console
✓ Fill out metadata
✓ Submit (faster: 2–4 hours usually)
```

### Managing Multiple Versions

```
If supporting iOS 15 + 16 + 17:
- Minimum deployment target: iOS 15 (oldest supported)
- SwiftUI works on iOS 15+ (use conditional compilation for iOS 17 features)
- Test on at least 2 device models (iPhone 12 Mini, iPhone 14 Pro)

If supporting Android 8+ (API 26+):
- Use Compose (requires API 21+)
- Handle old devices: disable features if needed
- Test on emulator + real device
```

---

## MOBILE STACK RECOMMENDATIONS BY SCENARIO

Real-world examples to guide your decision.

### Scenario 1: Social App (Instagram-like)

**Requirements:** Real-time updates, media heavy, notifications, discovery feed.

**Recommended Stack:**
```yaml
Framework: Expo (React Native)
UI: Expo UI + custom components
Database: Supabase (real-time posts)
Auth: Clerk or Supabase Auth
Storage: Cloudflare R2 (images, optimized delivery)
Real-time: Supabase Realtime (feed updates)
Push Notifications: Firebase Cloud Messaging
Analytics: Amplitude or PostHog
Hosting: EAS Build
Cost: $0–50/mo (MVP) → $150–250/mo (growth)
Timeline: 4–5 weeks
Team: 2–3 developers
```

**Why this stack:**
- Expo is fast to iterate (HMR, EAS Build handles publishing)
- Supabase real-time is ideal for social feeds
- Cloudflare R2 for images (cheap, fast)
- Firebase push is free and reliable

### Scenario 2: Productivity App (Notion-like, Offline-first)

**Requirements:** Offline editing, sync when online, collaborative, rich text.

**Recommended Stack:**
```yaml
Framework: Expo or Flutter
UI: Expo UI (for collaborative features, easier React context)
Database (Local): WatermelonDB (SQLite)
Database (Cloud): Supabase or custom API
Sync: PowerSync or custom sync logic
Auth: Clerk
Real-time: Supabase Realtime or custom WebSocket
Monitoring: Sentry
Cost: $50–150/mo (PowerSync) or $25–100/mo (custom)
Timeline: 5–6 weeks
Team: 2–4 developers
Complexity: High (offline-first is complex)
```

**Why this stack:**
- PowerSync handles offline/sync complexity
- Supabase for database (PostgreSQL flexibility)
- Expo for iteration speed (even with complexity)
- Rich text library: lexical or slate (complicated to set up, but necessary)

### Scenario 3: Fintech App (Secure, Real-time Trading)

**Requirements:** Security critical, real-time data, fast transactions, biometric auth.

**Recommended Stack:**
```yaml
Framework: Native (Swift + Kotlin) or Expo with native modules
UI: SwiftUI + Jetpack Compose (platform-specific)
Backend: Custom API (Node.js or Go)
Database: PostgreSQL (Neon or AWS RDS)
Auth: WorkOS (SSO, enterprise features) + Biometric (native)
Payments: Stripe API (backend handles it)
Real-time: WebSocket (custom or Socket.io)
Monitoring: DataDog + Sentry
Security: Jailbreak detection, encryption at rest
Cost: $200–500/mo
Timeline: 6–8 weeks
Team: 3–5 developers (security expertise needed)
Compliance: Consult lawyers (GDPR, financial regulations)
```

**Why this stack:**
- Security > flexibility: Native code allows encryption, biometric, jailbreak detection
- Real-time: WebSocket for price updates
- Custom backend: Full control over financial transactions
- Separate iOS + Android: Different security requirements per platform

### Scenario 4: E-commerce App

**Requirements:** Product catalog, shopping cart, payments, push notifications.

**Recommended Stack:**
```yaml
Framework: Expo (React Native)
UI: Expo UI + shadcn-inspired design
Database: Supabase (products, orders)
Auth: Clerk
Payments: Stripe (backend handles it)
Cart: Zustand state management
Product Search: Algolia or Meilisearch
Push: Firebase Cloud Messaging
Analytics: Segment + Amplitude
Monitoring: Sentry
Hosting: EAS Build
Cost: $50–150/mo
Timeline: 4–5 weeks
Team: 2–3 developers
```

**Why this stack:**
- Expo quick to market
- Supabase for product catalog
- Stripe handles payments securely
- Firebase push for notifications

### Scenario 5: Fitness/Health Tracking

**Requirements:** Sensor access (heart rate, GPS), offline, sync, wearable integration.

**Recommended Stack:**
```yaml
Framework: Native (for sensor access) or Expo with custom modules
UI: SwiftUI + Jetpack Compose
Database (Local): SQLite (Room for Android, SwiftData for iOS)
Database (Cloud): PostgreSQL + custom API
Wearable: Apple HealthKit + Google Fit integration
Sync: Custom background sync
Auth: Clerk or custom
Analytics: Segment
Monitoring: Sentry
Cost: $100–200/mo
Timeline: 6–8 weeks
Team: 2 devs per platform (iOS + Android)
Complexity: High (sensors, wearables, background processing)
```

**Why this stack:**
- HealthKit/Fit are platform-specific (must use native)
- SQLite local for sensor data (offline critical)
- Custom API for sync logic (health data is sensitive)
- Separate iOS + Android: Different sensor APIs

---

## MOBILE APP DECISION TREE SUMMARY

```
START: What kind of mobile app?
│
├─ SIMPLE (Info, forms, CRUD)
│  └─ Can skip app store? (Internal only)
│     ├─ YES → PWA ($0/mo, no app review)
│     └─ NO → Continue...
│
├─ PWA Suitable?
│  ├─ YES → PWA ($0/mo, 2–3 weeks)
│  └─ NO → Continue...
│
├─ Need to work offline?
│  ├─ YES → Native or Expo + WatermelonDB
│  └─ NO → Continue...
│
├─ Timeline critical (<4 weeks)?
│  ├─ YES → Expo (React Native)
│  └─ NO → Continue...
│
├─ Team has React experience?
│  ├─ YES → Expo ($0–150/mo)
│  ├─ NO → Use Flutter ($0–175/mo)
│  └─ Starting fresh? → Flutter (better performance, smaller apps)
│
├─ Extreme performance needed? (Games, AR, 60fps animations)
│  ├─ YES → Native (Swift/Kotlin) ($100–300/mo)
│  └─ NO → Expo or Flutter is fine
│
├─ Need specific platforms?
│  ├─ iOS only → Native Swift (cheaper, simpler)
│  ├─ Android only → Native Kotlin (cheapest)
│  └─ Both → Expo or Flutter (shared codebase)
│
└─ Real-time collaborative features?
   ├─ YES → Expo + PowerSync ($50–150/mo)
   └─ NO → Expo + Supabase ($0–50/mo)
```

---

## MOBILE APP COST ESTIMATION

| Stage | Scenario | Monthly Cost | Annual Cost |
|-------|----------|-------------|-----------|
| **MVP (0 users)** | Expo + Supabase Free | $0 | $99 (Apple Dev) |
| **Launch (100–1k)** | Expo + Supabase Free | $0–20 | $119–120 |
| **Growing (1k–10k)** | Expo + Supabase Pro + Firebase | $25–75 | $324–975 |
| **Scaling (10k–100k)** | Expo + Neon + Clerk + Monitoring | $100–250 | $1299–3099 |
| **Large (100k+)** | Custom API + Datadog + team | $500+/mo | $6000+/year |

---

## COMMON MOBILE MISTAKES

1. **Choosing cross-platform for performance-critical apps** — Use native for games, AR, animations
2. **Firebase lock-in** — Plan to migrate backend at $50k/mo revenue
3. **Ignoring iOS push limitations** — PWA push doesn't work well on iOS
4. **Not budgeting for EAS Build ($99/mo)** — Free tier exhausted quickly
5. **Forgetting app store fees** — Apple $99/year, Google $25 one-time (ongoing costs)
6. **Overbuilding before launch** — Ship MVP in 4 weeks, iterate based on feedback
7. **Not handling offline** — Users expect apps to work offline
8. **Security last-minute** — Plan security from day 1 (encryption, biometric auth)
