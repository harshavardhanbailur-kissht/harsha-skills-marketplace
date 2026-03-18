# Project Setup & Developer Experience

## Table of Contents
- [Scaffolding New Projects](#scaffolding-new-projects)
- [Monorepo Strategies](#monorepo-strategies)
- [Linting & Code Quality](#linting--code-quality)
- [Git Hooks](#git-hooks)
- [Environment Configuration](#environment-configuration)
- [Debugging Tools](#debugging-tools)
- [Hot Reload & Fast Iteration](#hot-reload--fast-iteration)
- [Package Management Best Practices](#package-management-best-practices)

## Scaffolding New Projects

### React Native (Expo)

```bash
# Recommended: Expo managed workflow
npx create-expo-app@latest MyApp --template tabs
cd MyApp

# Directory structure
MyApp/
├── app/                    # Expo Router file-based routing
│   ├── (tabs)/             # Tab navigator group
│   │   ├── index.tsx       # Home tab
│   │   ├── explore.tsx     # Explore tab
│   │   └── _layout.tsx     # Tab layout config
│   ├── _layout.tsx         # Root layout
│   └── +not-found.tsx      # 404 page
├── assets/                 # Images, fonts
├── components/             # Shared components
├── constants/              # Theme, config
├── hooks/                  # Custom hooks
├── app.json                # Expo config
├── tsconfig.json
└── package.json

# Expo with development build (for native modules)
npx create-expo-app MyApp
npx expo install expo-dev-client
npx expo run:ios    # Creates native build
```

### Flutter

```bash
flutter create --org com.example --platforms ios,android my_app
cd my_app

# Recommended structure (feature-first)
my_app/
├── lib/
│   ├── main.dart
│   ├── app/
│   │   ├── app.dart                 # MaterialApp, routing
│   │   └── theme.dart               # ThemeData
│   ├── core/
│   │   ├── constants/
│   │   ├── errors/                  # Failure classes
│   │   ├── network/                 # Dio client, interceptors
│   │   ├── storage/                 # Shared preferences, secure storage
│   │   └── utils/
│   ├── features/
│   │   ├── auth/
│   │   │   ├── data/
│   │   │   │   ├── datasources/
│   │   │   │   ├── models/
│   │   │   │   └── repositories/
│   │   │   ├── domain/
│   │   │   │   ├── entities/
│   │   │   │   ├── repositories/
│   │   │   │   └── usecases/
│   │   │   └── presentation/
│   │   │       ├── providers/       # Riverpod providers
│   │   │       ├── screens/
│   │   │       └── widgets/
│   │   ├── home/
│   │   └── settings/
│   └── shared/
│       ├── widgets/
│       └── extensions/
├── test/
├── integration_test/
├── pubspec.yaml
└── analysis_options.yaml
```

### Native iOS (Swift)

```bash
# Via Xcode → File → New → Project → App
# Or Swift Package Manager for libraries
mkdir MyApp && cd MyApp
swift package init --type executable

# Recommended Xcode project structure
MyApp/
├── MyApp/
│   ├── App/
│   │   ├── MyAppApp.swift           # @main entry
│   │   └── AppDelegate.swift        # If needed for push etc.
│   ├── Features/
│   │   ├── Auth/
│   │   │   ├── Views/
│   │   │   ├── ViewModels/
│   │   │   └── Models/
│   │   ├── Home/
│   │   └── Settings/
│   ├── Core/
│   │   ├── Network/
│   │   │   ├── APIClient.swift
│   │   │   └── Endpoints.swift
│   │   ├── Storage/
│   │   ├── Extensions/
│   │   └── Utilities/
│   ├── Shared/
│   │   ├── Components/
│   │   └── Modifiers/
│   ├── Resources/
│   │   ├── Assets.xcassets
│   │   └── Localizable.xcstrings
│   └── Info.plist
├── MyAppTests/
├── MyAppUITests/
└── MyApp.xcodeproj
```

### Native Android (Kotlin)

```bash
# Via Android Studio → New Project → Empty Activity (Compose)

# Recommended structure
app/
├── src/main/
│   ├── kotlin/com/example/myapp/
│   │   ├── MyApplication.kt         # Application class (Hilt)
│   │   ├── MainActivity.kt
│   │   ├── navigation/
│   │   │   ├── NavGraph.kt
│   │   │   └── Routes.kt
│   │   ├── features/
│   │   │   ├── auth/
│   │   │   │   ├── data/
│   │   │   │   │   ├── remote/      # API service, DTOs
│   │   │   │   │   ├── local/       # Room DAOs, entities
│   │   │   │   │   └── repository/  # Repository impl
│   │   │   │   ├── domain/
│   │   │   │   │   ├── model/       # Domain models
│   │   │   │   │   ├── repository/  # Repository interface
│   │   │   │   │   └── usecase/
│   │   │   │   └── ui/
│   │   │   │       ├── LoginScreen.kt
│   │   │   │       └── LoginViewModel.kt
│   │   │   ├── home/
│   │   │   └── settings/
│   │   ├── core/
│   │   │   ├── di/                  # Hilt modules
│   │   │   ├── network/
│   │   │   ├── database/
│   │   │   └── util/
│   │   └── ui/
│   │       ├── theme/
│   │       │   ├── Theme.kt
│   │       │   ├── Color.kt
│   │       │   └── Type.kt
│   │       └── components/          # Shared composables
│   ├── res/
│   └── AndroidManifest.xml
├── src/test/                        # Unit tests
├── src/androidTest/                 # Instrumentation tests
└── build.gradle.kts
```

---

## Monorepo Strategies

### Turborepo (React Native + Web)

```
my-monorepo/
├── apps/
│   ├── mobile/                # React Native (Expo)
│   │   ├── app/
│   │   └── package.json
│   ├── web/                   # Next.js
│   │   ├── app/
│   │   └── package.json
│   └── admin/                 # Admin dashboard
├── packages/
│   ├── ui/                    # Shared components (React Native Web)
│   │   ├── src/
│   │   │   ├── Button.tsx
│   │   │   └── Card.tsx
│   │   └── package.json
│   ├── api-client/            # Shared API client
│   │   ├── src/
│   │   └── package.json
│   ├── types/                 # Shared TypeScript types
│   └── config/
│       ├── eslint/
│       └── typescript/
├── turbo.json
├── package.json
└── pnpm-workspace.yaml
```

```json
// turbo.json
{
  "$schema": "https://turbo.build/schema.json",
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**", ".expo/**"]
    },
    "dev": { "cache": false, "persistent": true },
    "lint": { "dependsOn": ["^build"] },
    "test": { "dependsOn": ["build"] }
  }
}
```

```yaml
# pnpm-workspace.yaml
packages:
  - "apps/*"
  - "packages/*"
```

### Melos (Flutter Monorepo)

```yaml
# melos.yaml
name: my_workspace
packages:
  - apps/*
  - packages/*

scripts:
  analyze: melos exec -- flutter analyze
  test: melos exec -- flutter test
  build:android: melos exec --scope="mobile_app" -- flutter build apk
  build:ios: melos exec --scope="mobile_app" -- flutter build ipa
  clean: melos exec -- flutter clean
```

---

## Linting & Code Quality

### ESLint + Prettier (React Native)

```javascript
// .eslintrc.js
module.exports = {
  root: true,
  extends: [
    'expo',
    '@react-native',
    'plugin:@typescript-eslint/recommended',
    'prettier',
  ],
  plugins: ['@typescript-eslint', 'import'],
  rules: {
    'import/order': ['error', {
      groups: ['builtin', 'external', 'internal', 'parent', 'sibling', 'index'],
      'newlines-between': 'always',
      alphabetize: { order: 'asc' },
    }],
    '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
    'no-console': ['warn', { allow: ['warn', 'error'] }],
    'react/react-in-jsx-scope': 'off',
  },
};
```

```json
// .prettierrc
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "all",
  "printWidth": 100,
  "bracketSpacing": true
}
```

### Flutter Analysis Options

```yaml
# analysis_options.yaml
include: package:flutter_lints/flutter.yaml

analyzer:
  errors:
    missing_required_param: error
    missing_return: error
  exclude:
    - "**/*.g.dart"
    - "**/*.freezed.dart"

linter:
  rules:
    - always_declare_return_types
    - avoid_print
    - avoid_relative_lib_imports
    - cancel_subscriptions
    - close_sinks
    - prefer_const_constructors
    - prefer_const_declarations
    - prefer_final_fields
    - prefer_final_locals
    - require_trailing_commas
    - sort_constructors_first
    - use_key_in_widget_constructors
```

### Ktlint / Detekt (Android)

```kotlin
// build.gradle.kts (project level)
plugins {
    id("io.gitlab.arturbosch.detekt") version "1.23.6"
}

detekt {
    config.setFrom("$rootDir/config/detekt.yml")
    buildUponDefaultConfig = true
    allRules = false
}
```

```yaml
# config/detekt.yml
complexity:
  LongMethod:
    threshold: 30
  LongParameterList:
    functionThreshold: 6
    constructorThreshold: 8
naming:
  FunctionNaming:
    functionPattern: '[a-z][a-zA-Z0-9]*'
  TopLevelPropertyNaming:
    constantPattern: '[A-Z][A-Za-z0-9]*'
style:
  MagicNumber:
    active: true
    ignoreNumbers: ['-1', '0', '1', '2']
  MaxLineLength:
    maxLineLength: 120
```

### SwiftLint (iOS)

```yaml
# .swiftlint.yml
included:
  - MyApp
excluded:
  - MyApp/Generated
  - Pods
disabled_rules:
  - trailing_whitespace
opt_in_rules:
  - closure_end_indentation
  - closure_spacing
  - collection_alignment
  - contains_over_filter_count
  - empty_count
  - force_unwrapping
  - implicitly_unwrapped_optional
  - missing_docs
  - multiline_parameters
  - vertical_parameter_alignment_on_call
line_length:
  warning: 120
  error: 200
type_body_length:
  warning: 300
  error: 500
file_length:
  warning: 500
  error: 1000
```

---

## Git Hooks

### Husky + lint-staged (React Native)

```json
// package.json
{
  "scripts": {
    "prepare": "husky"
  },
  "lint-staged": {
    "*.{ts,tsx}": [
      "eslint --fix",
      "prettier --write"
    ],
    "*.{json,md}": "prettier --write"
  }
}
```

```bash
# .husky/pre-commit
pnpm lint-staged

# .husky/commit-msg
npx commitlint --edit $1
```

```javascript
// commitlint.config.js
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [2, 'always', [
      'feat', 'fix', 'docs', 'style', 'refactor',
      'perf', 'test', 'build', 'ci', 'chore', 'revert',
    ]],
    'subject-max-length': [2, 'always', 72],
  },
};
```

### Pre-commit for Flutter/Native

```yaml
# .pre-commit-config.yaml (Python pre-commit framework)
repos:
  - repo: local
    hooks:
      - id: flutter-analyze
        name: Flutter Analyze
        entry: flutter analyze
        language: system
        types: [dart]
      - id: flutter-format
        name: Flutter Format
        entry: dart format --set-exit-if-changed .
        language: system
        types: [dart]
      - id: flutter-test
        name: Flutter Test
        entry: flutter test
        language: system
        pass_filenames: false
```

---

## Environment Configuration

### React Native (.env)

```bash
# .env.development
API_URL=https://dev-api.example.com
SENTRY_DSN=https://dev@sentry.io/123
FEATURE_FLAG_NEW_ONBOARDING=true

# .env.staging
API_URL=https://staging-api.example.com

# .env.production
API_URL=https://api.example.com
```

```typescript
// Using expo-constants + app.config.ts
export default ({ config }) => ({
  ...config,
  extra: {
    apiUrl: process.env.API_URL ?? 'https://api.example.com',
    sentryDsn: process.env.SENTRY_DSN,
    eas: { projectId: 'your-project-id' },
  },
});

// Access in code
import Constants from 'expo-constants';
const API_URL = Constants.expoConfig?.extra?.apiUrl;
```

### Flutter (dart-define)

```bash
# Pass at build time
flutter run --dart-define=API_URL=https://dev-api.example.com
flutter build apk --dart-define-from-file=env/production.json
```

```json
// env/production.json
{
  "API_URL": "https://api.example.com",
  "SENTRY_DSN": "https://prod@sentry.io/123",
  "ENABLE_ANALYTICS": "true"
}
```

```dart
class EnvConfig {
  static const apiUrl = String.fromEnvironment('API_URL', defaultValue: 'https://api.example.com');
  static const sentryDsn = String.fromEnvironment('SENTRY_DSN');
  static const enableAnalytics = bool.fromEnvironment('ENABLE_ANALYTICS', defaultValue: false);
}
```

### Android (BuildConfig + Flavors)

```kotlin
// build.gradle.kts (app)
android {
    buildTypes {
        debug {
            buildConfigField("String", "API_URL", "\"https://dev-api.example.com\"")
        }
        release {
            buildConfigField("String", "API_URL", "\"https://api.example.com\"")
            isMinifyEnabled = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }
    flavorDimensions += "environment"
    productFlavors {
        create("staging") {
            dimension = "environment"
            applicationIdSuffix = ".staging"
            buildConfigField("String", "API_URL", "\"https://staging-api.example.com\"")
        }
        create("production") {
            dimension = "environment"
        }
    }
}
```

### iOS (Xcode Configurations + xcconfig)

```
// Config/Dev.xcconfig
API_URL = https:/$()/dev-api.example.com
BUNDLE_ID_SUFFIX = .dev
PRODUCT_NAME = MyApp Dev

// Config/Prod.xcconfig
API_URL = https:/$()/api.example.com
BUNDLE_ID_SUFFIX =
PRODUCT_NAME = MyApp
```

```swift
// Access via Info.plist
enum Config {
    static var apiURL: String {
        Bundle.main.infoDictionary?["API_URL"] as? String ?? ""
    }
}
```

---

## Debugging Tools

### React Native

```bash
# Flipper (deprecated) → Use React Native DevTools
npx react-native start    # Metro bundler with DevTools

# React DevTools
npx react-devtools        # Standalone component inspector

# Network debugging
# Use Reactotron
npm install reactotron-react-native --save-dev
```

```typescript
// reactotron.config.ts
import Reactotron from 'reactotron-react-native';
import { QueryClientManager, reactotronReactQuery } from 'reactotron-react-query';

const queryClientManager = new QueryClientManager({});

Reactotron.configure({ name: 'MyApp' })
  .useReactNative()
  .use(reactotronReactQuery(queryClientManager))
  .connect();
```

### Flutter

```bash
# Flutter DevTools (built in)
flutter pub global activate devtools
dart devtools

# Features: Widget Inspector, Performance, Memory, Network, Logging

# Debug logging
import 'dart:developer';
log('User loaded', name: 'UserRepository', error: exception);
```

### Native — Instruments (iOS) & Android Profiler

```swift
// Signposts for custom profiling (iOS)
import os

let signpostLog = OSLog(subsystem: "com.example.myapp", category: "networking")
let signpostID = OSSignpostID(log: signpostLog)

os_signpost(.begin, log: signpostLog, name: "API Call", signpostID: signpostID)
// ... network call ...
os_signpost(.end, log: signpostLog, name: "API Call", signpostID: signpostID)
```

```kotlin
// Custom trace (Android)
import androidx.tracing.trace

trace("loadUsers") {
    val users = repository.getUsers()
    _state.value = UiState.Success(users)
}
```

---

## Hot Reload & Fast Iteration

| Framework | Hot Reload | Stateful | Speed |
|-----------|-----------|----------|-------|
| React Native (Metro) | Fast Refresh | Yes (preserves state) | ~200ms |
| Flutter | Hot Reload | Yes | ~300ms |
| Flutter | Hot Restart | No (resets state) | ~1s |
| SwiftUI (Xcode) | Preview | Partial | Variable |
| Compose (Android Studio) | Live Edit | Partial | ~1-3s |
| Capacitor | Live Reload | No | ~1s |

### Best Practices for Fast Iteration

1. **Use emulators/simulators for rapid dev** — Real devices for final testing
2. **Keep build times low** — Modularize, use incremental builds, cache dependencies
3. **Leverage platform previews** — SwiftUI Previews, Compose @Preview, Storybook (RN)
4. **Use mock data during development** — Don't depend on live APIs for UI work
5. **Profile startup time regularly** — It creeps up without monitoring

---

## Package Management Best Practices

### React Native

```json
// Use exact versions for native-dependent packages
{
  "dependencies": {
    "expo": "~51.0.0",
    "react-native-reanimated": "~3.10.0",
    "react-native-gesture-handler": "~2.16.0"
  },
  "resolutions": {
    // Force specific versions to avoid conflicts
    "react-native": "0.74.5"
  }
}
```

### Flutter

```yaml
# pubspec.yaml — use version constraints
dependencies:
  flutter:
    sdk: flutter
  dio: ^5.4.0              # Compatible with 5.x
  riverpod: ^2.5.0
  go_router: ^14.0.0
  freezed_annotation: ^2.4.0

dev_dependencies:
  flutter_test:
    sdk: flutter
  build_runner: ^2.4.0
  freezed: ^2.5.0
  json_serializable: ^6.8.0
  mockito: ^5.4.0
  flutter_lints: ^4.0.0

# Lock file: pubspec.lock (commit this!)
```

### iOS (SPM)

```swift
// Package.swift (for libraries) or Xcode SPM UI
dependencies: [
    .package(url: "https://github.com/Alamofire/Alamofire.git", from: "5.9.0"),
    .package(url: "https://github.com/pointfreeco/swift-composable-architecture", from: "1.12.0"),
]
```

### Android (Version Catalogs)

```toml
# gradle/libs.versions.toml
[versions]
kotlin = "2.0.0"
compose-bom = "2024.06.00"
hilt = "2.51.1"
retrofit = "2.11.0"
room = "2.6.1"

[libraries]
compose-bom = { group = "androidx.compose", name = "compose-bom", version.ref = "compose-bom" }
compose-material3 = { group = "androidx.compose.material3", name = "material3" }
hilt-android = { group = "com.google.dagger", name = "hilt-android", version.ref = "hilt" }
room-runtime = { group = "androidx.room", name = "room-runtime", version.ref = "room" }
room-ktx = { group = "androidx.room", name = "room-ktx", version.ref = "room" }

[plugins]
kotlin-android = { id = "org.jetbrains.kotlin.android", version.ref = "kotlin" }
hilt = { id = "com.google.dagger.hilt.android", version.ref = "hilt" }
```

```kotlin
// build.gradle.kts
dependencies {
    implementation(platform(libs.compose.bom))
    implementation(libs.compose.material3)
    implementation(libs.hilt.android)
    implementation(libs.room.runtime)
    implementation(libs.room.ktx)
}
```
