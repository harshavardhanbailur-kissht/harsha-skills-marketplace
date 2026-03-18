# Mobile CI/CD & DevOps Reference

Comprehensive guide for implementing continuous integration and deployment pipelines for iOS and Android applications.

## Table of Contents

- [1. CI/CD Platforms Comparison](#1-cicd-platforms-comparison)
- [2. GitHub Actions Workflows for iOS and Android](#2-github-actions-workflows-for-ios-and-android)
- [3. Fastlane Setup - Fastfile Configuration](#3-fastlane-setup---fastfile-configuration)
- [4. Code Signing & Certificates](#4-code-signing--certificates)
- [5. Automated Testing in CI Pipelines](#5-automated-testing-in-ci-pipelines)
- [6. App Distribution Strategies](#6-app-distribution-strategies)
- [7. Release Management](#7-release-management)
- [8. Environment Management](#8-environment-management)
- [9. Branching Strategies](#9-branching-strategies)
- [10. OTA Updates](#10-ota-updates)
- [11. App Store & Play Store Submission](#11-app-store--play-store-submission)
- [12. Monitoring & Crash Reporting Integration](#12-monitoring--crash-reporting-integration)

## 1. CI/CD Platforms Comparison

### GitHub Actions
- **Cost**: Free for public repos, included minutes for private
- **Best for**: GitHub-hosted projects, tight GitHub integration
- **Strengths**: Native GitHub integration, marketplace ecosystem, no external account needed
- **Limitations**: Limited iOS runner options, requires macOS runners for Apple builds
- **Pricing**: 3,000/month free minutes for private repos

### Bitrise
- **Cost**: Freemium ($99-249/month for teams)
- **Best for**: Mobile-first, complex workflows
- **Strengths**: Pre-configured mobile stacks, excellent iOS/Android support, visual workflow builder
- **Limitations**: Proprietary, higher cost for advanced features
- **Features**: In-app testing, deployment management, artifact management

### Codemagic
- **Cost**: Freemium ($50-299/month)
- **Best for**: Flutter-first teams, fast builds
- **Strengths**: Optimized for Flutter, very fast macOS runners, comprehensive testing
- **Limitations**: Less mature for native development
- **Features**: Automated testing, notarization, App Store Connect automation

### CircleCI
- **Cost**: Freemium ($15-150/month)
- **Best for**: Teams wanting container-based CI/CD
- **Strengths**: Powerful compute, excellent parallelization, extensive integrations
- **Limitations**: Steeper learning curve, complex configuration
- **Features**: SSH debugging, resource classes, Docker support

## 2. GitHub Actions Workflows for iOS and Android

### iOS Build Workflow

```yaml
name: iOS Build & Deploy

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ develop ]
  workflow_dispatch:
    inputs:
      build_type:
        description: 'Build type'
        required: true
        default: 'beta'

env:
  DEVELOPER_DIR: /Applications/Xcode_15.0.app/Contents/Developer
  FASTLANE_USER: ${{ secrets.APPLE_ID }}
  FASTLANE_PASSWORD: ${{ secrets.APPLE_ID_PASSWORD }}

jobs:
  build:
    runs-on: macos-14
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Ruby
        uses: ruby/setup-ruby@v1
        with:
          ruby-version: '3.3'
          bundler-cache: true

      - name: Install dependencies
        run: |
          cd ios
          pod install

      - name: Set build number
        run: |
          BUILD_NUMBER=${{ github.run_number }}
          echo "BUILD_NUMBER=$BUILD_NUMBER" >> $GITHUB_ENV

      - name: Decrypt code signing files
        run: |
          cd ios
          ./scripts/decrypt_certs.sh ${{ secrets.ENCRYPTION_PASSWORD }}

      - name: Build with Fastlane
        run: |
          cd ios
          bundle exec fastlane build_release \
            version:${{ github.ref_name }} \
            build_number:$BUILD_NUMBER

      - name: Upload to TestFlight
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        run: |
          cd ios
          bundle exec fastlane beta

      - name: Upload artifacts
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: ios-build-artifacts
          path: ios/build/**/*.ipa

      - name: Notify Slack on failure
        if: failure()
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: 'iOS build failed'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}

  test:
    runs-on: macos-14
    needs: build
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Run tests
        run: |
          cd ios
          xcodebuild test \
            -workspace MyApp.xcworkspace \
            -scheme MyApp \
            -destination 'generic/platform=iOS' \
            -resultBundlePath test-results

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./ios/test-results/CodeCoverage.json

  lint:
    runs-on: macos-14
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Run SwiftLint
        run: |
          brew install swiftlint
          swiftlint lint ios/
```

### Android Build Workflow

```yaml
name: Android Build & Deploy

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ develop ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up JDK
        uses: actions/setup-java@v3
        with:
          java-version: '17'
          distribution: 'temurin'
          cache: gradle

      - name: Decode signing key
        run: |
          echo ${{ secrets.ANDROID_SIGNING_KEY_B64 }} | base64 -d > android/keystore.jks
          echo "KEYSTORE_PATH=${{ github.workspace }}/android/keystore.jks" >> $GITHUB_ENV

      - name: Build APK
        run: |
          cd android
          ./gradlew assembleRelease \
            -Pandroid.signingConfig.storePath=$KEYSTORE_PATH \
            -Pandroid.signingConfig.storePassword=${{ secrets.ANDROID_KEYSTORE_PASSWORD }} \
            -Pandroid.signingConfig.keyAlias=${{ secrets.ANDROID_KEY_ALIAS }} \
            -Pandroid.signingConfig.keyPassword=${{ secrets.ANDROID_KEY_PASSWORD }}

      - name: Build Bundle
        run: |
          cd android
          ./gradlew bundleRelease

      - name: Upload to Firebase App Distribution
        if: github.event_name == 'push' && github.ref == 'refs/heads/develop'
        run: |
          cd android
          bundle exec fastlane beta

      - name: Upload to Play Store
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        run: |
          cd android
          bundle exec fastlane release

      - name: Upload artifacts
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: android-build-artifacts
          path: |
            android/app/build/outputs/apk/**/*.apk
            android/app/build/outputs/bundle/**/*.aab

  test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up JDK
        uses: actions/setup-java@v3
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Run unit tests
        run: |
          cd android
          ./gradlew testDebugUnitTest

      - name: Run instrumented tests
        uses: reactivecircus/android-emulator-runner@v2
        with:
          api-level: 31
          script: cd android && ./gradlew connectedDebugAndroidTest

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## 3. Fastlane Setup - Fastfile Configuration

### iOS Fastfile

```ruby
# ios/fastlane/Fastfile

default_platform(:ios)

platform :ios do
  desc "Build for release"
  lane :build_release do |options|
    version = options[:version] || get_version_number(xcodeproj: "MyApp.xcodeproj")
    build_number = options[:build_number] || get_build_number(xcodeproj: "MyApp.xcodeproj")

    increment_version_number(
      version_number: version,
      xcodeproj: "MyApp.xcodeproj"
    )

    increment_build_number(
      build_number: build_number,
      xcodeproj: "MyApp.xcodeproj"
    )

    build_app(
      workspace: "MyApp.xcworkspace",
      scheme: "MyApp",
      configuration: "Release",
      output_directory: "build",
      output_name: "MyApp.ipa",
      export_method: "app-store",
      codesigning_identity: "Apple Distribution: Company Name",
      code_signing_style: "automatic"
    )
  end

  desc "Upload beta to TestFlight"
  lane :beta do
    build_release

    upload_to_testflight(
      app_identifier: "com.company.myapp",
      ipa: "build/MyApp.ipa",
      skip_waiting_for_build_processing: true,
      skip_submission: false,
      beta_app_review_info: {
        contact_email: "beta@company.com",
        contact_first_name: "Beta",
        contact_last_name: "Team",
        contact_phone: "+1234567890",
        demo_account_name: "demo@example.com",
        demo_account_password: "password",
        notes: "Beta release"
      }
    )

    notify_slack(message: "iOS beta uploaded successfully")
  end

  desc "Release to App Store"
  lane :release do
    build_release

    upload_to_app_store(
      app_identifier: "com.company.myapp",
      ipa: "build/MyApp.ipa",
      skip_binary_upload: false,
      force: true,
      submit_for_review: true,
      automatic_release: false,
      submission_information: {
        add_id_info_uses_idfa: true
      }
    )

    notify_slack(message: "iOS released to App Store")
  end

  desc "Sync code signing with Match"
  lane :sync_certificates do
    match(
      type: "appstore",
      app_identifier: "com.company.myapp",
      git_url: "https://github.com/company/certificates.git",
      git_branch: "master",
      readonly: false,
      username: ENV["APPLE_ID"]
    )
  end

  desc "Run tests"
  lane :test do
    run_tests(
      workspace: "MyApp.xcworkspace",
      scheme: "MyApp",
      devices: ["iPhone 15"],
      configuration: "Debug",
      code_coverage: true,
      xcargs: "-enableCodeCoverage YES",
      output_directory: "test-results",
      output_types: "json,html"
    )
  end

  private_lane :notify_slack do |options|
    slack(
      message: options[:message],
      slack_url: ENV["SLACK_WEBHOOK"],
      success: true
    )
  end
end
```

### Android Fastfile

```ruby
# android/fastlane/Fastfile

default_platform(:android)

platform :android do
  desc "Build release APK"
  lane :build_release do
    gradle(
      project_dir: "android/",
      task: "clean assembleRelease",
      properties: {
        "android.injected.signing.store.file" => ENV["KEYSTORE_PATH"],
        "android.injected.signing.store.password" => ENV["ANDROID_KEYSTORE_PASSWORD"],
        "android.injected.signing.key.alias" => ENV["ANDROID_KEY_ALIAS"],
        "android.injected.signing.key.password" => ENV["ANDROID_KEY_PASSWORD"]
      }
    )
  end

  desc "Build release AAB"
  lane :build_bundle do
    gradle(
      project_dir: "android/",
      task: "bundleRelease",
      properties: {
        "android.injected.signing.store.file" => ENV["KEYSTORE_PATH"],
        "android.injected.signing.store.password" => ENV["ANDROID_KEYSTORE_PASSWORD"],
        "android.injected.signing.key.alias" => ENV["ANDROID_KEY_ALIAS"],
        "android.injected.signing.key.password" => ENV["ANDROID_KEY_PASSWORD"]
      }
    )
  end

  desc "Upload beta to Firebase App Distribution"
  lane :beta do
    build_release
    apk_path = "android/app/build/outputs/apk/release/app-release.apk"

    firebase_app_distribution(
      app: ENV["FIREBASE_APP_ID"],
      apk_path: apk_path,
      testers: "qa@company.com",
      release_notes: ENV["RELEASE_NOTES"]
    )

    notify_slack(message: "Android beta uploaded to Firebase")
  end

  desc "Upload to Play Store internal testing"
  lane :internal_testing do
    build_bundle

    upload_to_play_store(
      track: "internal",
      aab: "android/app/build/outputs/bundle/release/app-release.aab",
      json_key_data: ENV["PLAY_STORE_JSON_KEY"]
    )

    notify_slack(message: "Android uploaded to Play Store internal testing")
  end

  desc "Release to Play Store"
  lane :release do
    build_bundle

    upload_to_play_store(
      track: "production",
      aab: "android/app/build/outputs/bundle/release/app-release.aab",
      json_key_data: ENV["PLAY_STORE_JSON_KEY"],
      skip_upload_aab: false,
      skip_upload_metadata: false,
      skip_upload_images: false,
      skip_upload_screenshots: false
    )

    notify_slack(message: "Android released to Play Store")
  end

  desc "Run unit tests"
  lane :test do
    gradle(
      project_dir: "android/",
      task: "testDebugUnitTest"
    )
  end

  private_lane :notify_slack do |options|
    slack(
      message: options[:message],
      slack_url: ENV["SLACK_WEBHOOK"]
    )
  end
end
```

## 4. Code Signing & Certificates

### iOS Code Signing with Match

```ruby
# Gemfile
gem 'match'
gem 'cert'
gem 'sigh'

# Setup Match
match(type: "appstore", force_for_new_devices: true)

# Match storage in private Git repo
# Using git storage for certificates and provisioning profiles
# Enterprise: Use S3 or Google Cloud Storage

# Fastfile integration
lane :sync_certs do
  match(
    type: "appstore",
    app_identifier: ["com.company.app", "com.company.app.widget"],
    git_url: "https://github.com/company/certificates.git",
    git_branch: "master",
    readonly: false
  )
end

# For CI: Use readonly + encrypted credentials
lane :setup_ci do
  setup_ci if is_ci
  match(
    type: "appstore",
    readonly: true,
    git_url: ENV["MATCH_GIT_URL"],
    git_branch: ENV["MATCH_BRANCH"]
  )
end
```

### Android Keystore Configuration

```gradle
// build.gradle (app level)

android {
    signingConfigs {
        release {
            storeFile file(System.getenv("KEYSTORE_PATH") ?: "debug.keystore")
            storePassword System.getenv("ANDROID_KEYSTORE_PASSWORD")
            keyAlias System.getenv("ANDROID_KEY_ALIAS")
            keyPassword System.getenv("ANDROID_KEY_PASSWORD")
        }
    }

    buildTypes {
        release {
            signingConfig signingConfigs.release
            minifyEnabled true
            shrinkResources true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
}
```

### Generating Android Keystore

```bash
#!/bin/bash
# Generate keystore for Android signing

keytool -genkey -v -keystore release.keystore \
    -keyalg RSA -keysize 2048 -validity 10000 \
    -alias production \
    -dname "CN=Company Name, OU=Mobile, O=Company, L=City, ST=State, C=Country"

# Encode for CI/CD storage
base64 -i release.keystore -o release.keystore.b64

# Store securely in CI secrets: ANDROID_SIGNING_KEY_B64
```

## 5. Automated Testing in CI Pipelines

### iOS Testing Strategy

```bash
#!/bin/bash
# Run tests with coverage

xcodebuild test \
    -workspace MyApp.xcworkspace \
    -scheme MyApp \
    -destination 'platform=iOS Simulator,name=iPhone 15' \
    -derivedDataPath build \
    -resultBundlePath test-results.xcresult \
    -enableCodeCoverage YES

# Generate coverage report
xcrun xccov view --report --json test-results.xcresult > coverage.json
```

### Android Testing Strategy

```gradle
// Run unit tests
./gradlew testDebugUnitTest --info

// Run instrumented tests on emulator
./gradlew connectedDebugAndroidTest

// Generate coverage report
./gradlew jacocoTestDebugUnitTestReport

// Output: build/reports/jacoco/jacocoTestDebugUnitTestReport/html/index.html
```

## 6. App Distribution Strategies

### TestFlight (iOS)

- Manual review: 24-48 hours
- Up to 10,000 external testers
- Automatically expires after 90 days
- Supports phased rollout during production release

### Firebase App Distribution (Android)

- Instant distribution to testers
- Testers join via email invitation
- No app review required
- Easy integration with CI/CD

### Play Store Internal Testing (Android)

- Private testing before release
- Minimum 14 hour review period
- Perfect for QA and early access
- Full Play Store functionality

## 7. Release Management

### Semantic Versioning

```
MAJOR.MINOR.PATCH
1.2.3

- MAJOR: Breaking changes
- MINOR: New features (backwards compatible)
- PATCH: Bug fixes
```

### Changelog Management

```markdown
# Changelog

## [1.2.0] - 2026-03-03
### Added
- Push notification support
- Dark mode theme

### Fixed
- Crash on app launch

### Changed
- Updated dependencies

## [1.1.0] - 2026-02-15
### Added
- User authentication
```

### Release Workflow

1. Create release branch from main: `release/1.2.0`
2. Update version, build number, changelog
3. Create release tag: `v1.2.0`
4. Merge back to main and develop
5. Trigger automated deployment

## 8. Environment Management

### Configuration by Environment

```swift
// iOS Config.swift
enum Environment {
    case development
    case staging
    case production

    var apiBaseURL: String {
        switch self {
        case .development:
            return "https://dev-api.example.com"
        case .staging:
            return "https://staging-api.example.com"
        case .production:
            return "https://api.example.com"
        }
    }

    var analyticsEnabled: Bool {
        return self != .development
    }
}
```

```kotlin
// Android Build variants
buildTypes {
    debug {
        buildConfigField "String", "API_BASE_URL", '"https://dev-api.example.com"'
    }
    staging {
        buildConfigField "String", "API_BASE_URL", '"https://staging-api.example.com"'
    }
    release {
        buildConfigField "String", "API_BASE_URL", '"https://api.example.com"'
    }
}
```

## 9. Branching Strategies

### GitFlow

```
main (production releases)
├── develop (integration branch)
    ├── feature/user-auth
    ├── feature/push-notifications
    ├── release/1.2.0
    └── hotfix/critical-bug
```

### Trunk-Based Development

```
main (always deployable)
├── feat/user-auth
├── fix/critical-bug
└── chore/dependencies
```

For mobile, GitFlow recommended due to:
- Longer release cycles
- Multiple concurrent versions in market
- Staged rollout requirements

## 10. OTA Updates

### EAS Update (React Native/Expo)

```bash
# Install EAS CLI
npm install -g eas-cli

# Configure project
eas update:configure

# Create update
eas update --branch production --message "Bug fixes"

# Publish update
eas build --platform ios --build-profile preview
eas submit -p ios --latest
```

### CodePush (React Native - Microsoft)

```bash
# Install AppCenter CLI
npm install -g appcenter-cli

# Create CodePush deployment
appcenter codepush deployment add --app mycompany/myapp Production

# Release update
appcenter codepush release-react \
    --app mycompany/myapp \
    --deployment-name Production \
    --description "Bug fixes"
```

## 11. App Store & Play Store Submission

### Automated App Store Submission

```ruby
lane :submit_app_store do
  upload_to_app_store(
    app_identifier: "com.company.app",
    ipa: "build/MyApp.ipa",
    skip_binary_upload: false,
    skip_metadata: false,
    submit_for_review: true,
    automatic_release: false,
    submission_information: {
      add_id_info_uses_idfa: true
    }
  )
end
```

### Automated Play Store Submission

```ruby
lane :submit_play_store do
  upload_to_play_store(
    track: "production",
    aab: "build/app-release.aab",
    json_key_data: ENV["PLAY_STORE_JSON_KEY"],
    rollout: 0.05  # 5% phased rollout
  )
end
```

## 12. Monitoring & Crash Reporting Integration

### Sentry Integration

```ruby
# iOS
lane :configure_sentry do
  sh("cd .. && sentry-cli releases files upload-sourcemaps ./build/Release-iphoneos/MyApp.app.dSYM/Contents/Resources/DWARF/MyApp")
end

# Android
lane :configure_sentry do
  gradle(
    project_dir: "android/",
    task: "sentryUploadProguardMappings"
  )
end
```

### Firebase Crashlytics

```swift
// iOS
import FirebaseCore
import FirebaseCrashlytics

FirebaseApp.configure()

// Automated error reporting
DispatchQueue.global(qos: .default).async {
    do {
        _ = try crashlytics.checkForUnsentReports()
    }
}
```

```kotlin
// Android
import com.google.firebase.crashlytics.ktx.crashlytics
import com.google.firebase.ktx.Firebase

Firebase.crashlytics.apply {
    setUserId(userId)
    setCustomKey("screen", "login")
}
```

### Analytics & Performance Monitoring

```swift
// Firebase Analytics (iOS)
Analytics.logEvent(AnalyticsEventAppOpen, parameters: [
    AnalyticsParameterSource: "push_notification"
])

// Performance monitoring
let trace = Performance.startTrace(name: "login_flow")
trace?.incrementMetric("successful_logins")
trace?.stop()
```

---

**Best Practices Summary**
- Automate everything from testing to release
- Use proper code signing and secret management
- Implement comprehensive monitoring from day one
- Plan branching strategy before first release
- Test all release automation on staging first
- Document environment-specific configurations
- Use semantic versioning consistently
- Maintain detailed changelog for every release
