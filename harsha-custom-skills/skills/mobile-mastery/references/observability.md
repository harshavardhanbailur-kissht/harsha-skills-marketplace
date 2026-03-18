# Mobile App Observability & Monitoring

## Table of Contents

- [1. Crash Reporting](#1-crash-reporting)
- [2. Performance Monitoring](#2-performance-monitoring)
- [3. Analytics](#3-analytics)
- [4. Logging](#4-logging)
- [5. Error Budgets & SLOs](#5-error-budgets--slos)
- [6. Feature Flags & Remote Config](#6-feature-flags--remote-config)
- [7. Alerting & On-Call](#7-alerting--on-call)
- [8. User Feedback & Session Replay](#8-user-feedback--session-replay)
- [9. Release Health Monitoring](#9-release-health-monitoring)
- [10. Privacy-Compliant Monitoring](#10-privacy-compliant-monitoring)

Comprehensive guide to implementing crash reporting, analytics, monitoring, logging, and observability across mobile platforms.

## 1. Crash Reporting

### Firebase Crashlytics

**React Native:**
```javascript
import crashlytics from '@react-native-firebase/crashlytics';

// Initialize
await crashlytics().setCrashlyticsCollectionEnabled(true);

// Log non-fatal errors
crashlytics().recordError(error, stackTrace);

// Add breadcrumbs
crashlytics().log('User initiated purchase flow');

// Add user context
crashlytics().setUserId('user-123');
crashlytics().setAttribute('subscription_tier', 'premium');

// Custom events
crashlytics().log('Custom event: Feature X used');
```

**Flutter:**
```dart
import 'package:firebase_crashlytics/firebase_crashlytics.dart';

// Initialize
FirebaseCrashlytics.instance.recordError(
  error,
  stackTrace,
  reason: 'Unhandled exception',
  fatal: true,
);

// Breadcrumbs
FirebaseCrashlytics.instance.log('User action: button tapped');

// User context
FirebaseCrashlytics.instance.setUserIdentifier('user-123');

// Custom keys
FirebaseCrashlytics.instance.setCustomKey('app_version', '2.1.0');
```

**iOS (Swift):**
```swift
import FirebaseCrashlytics

// Log non-fatal error
Crashlytics.crashlytics().record(error: error)

// Add breadcrumbs
Crashlytics.crashlytics().log("User started checkout")

// User context
Crashlytics.crashlytics().setUserID("user-123")
Crashlytics.crashlytics().setCustomValue("premium", forKey: "subscription_tier")
```

**Android (Kotlin):**
```kotlin
import com.google.firebase.crashlytics.FirebaseCrashlytics

// Record non-fatal exception
FirebaseCrashlytics.getInstance().recordException(exception)

// Add breadcrumb
FirebaseCrashlytics.getInstance().log("Payment processing started")

// User context
FirebaseCrashlytics.getInstance().setUserId("user-123")
FirebaseCrashlytics.getInstance().setCustomKey("subscription_tier", "premium")
```

### Sentry

**React Native:**
```javascript
import * as Sentry from "@sentry/react-native";

Sentry.init({
  dsn: "https://examplePublicKey@o0.ingest.sentry.io/0",
  integrations: [
    new Sentry.ReactNativeTracing(),
  ],
  tracesSampleRate: 0.1,
  environment: "production",
  debug: false,
});

// Capture exception
Sentry.captureException(error);

// Add breadcrumb
Sentry.addBreadcrumb({
  category: "user-action",
  message: "User tapped purchase button",
  level: "info",
});

// Set user context
Sentry.setUser({
  id: "user-123",
  username: "john_doe",
  email: "john@example.com",
});

// Source map upload: sentry-cli releases files upload-sourcemaps
```

**Flutter:**
```dart
import 'package:sentry_flutter/sentry_flutter.dart';

await SentryFlutter.init(
  (options) {
    options.dsn = 'https://examplePublicKey@o0.ingest.sentry.io/0';
    options.environment = 'production';
    options.tracesSampleRate = 0.1;
  },
  appRunner: () => runApp(MyApp()),
);

// Capture error
await Sentry.captureException(error, stackTrace: st);

// Add breadcrumb
Sentry.addBreadcrumb(Breadcrumb(
  message: 'User initiated checkout',
  category: 'user-action',
  level: SentryLevel.info,
));

// Set user context
Sentry.setUser(SentryUser(id: 'user-123', username: 'john_doe'));
```

### Crash-Free Rate Target: >99.5%
- **Formula:** (Total Sessions - Crash Sessions) / Total Sessions × 100
- **Monitoring:** Track daily, weekly, rolling 28-day windows
- **Alert threshold:** If crash-free rate drops below 98.5% in any hour

---

## 2. Performance Monitoring

### Firebase Performance Monitoring

**React Native:**
```javascript
import perf from '@react-native-firebase/perf';

// Custom trace
const trace = await perf().startTrace('checkout_flow');
trace.putMetric('item_count', 5);
trace.putAttribute('user_segment', 'premium');
await trace.stop();

// App startup monitoring (automatic)
// Network request monitoring
perf().newHttpMetric('https://api.example.com/users', 'GET')
  .start()
  .then(metric => {
    metric.setResponse(response);
    metric.stop();
  });

// Custom metrics
const trace = await perf().startTrace('api_call');
trace.putMetric('response_size', 2048);
trace.stop();
```

**Flutter:**
```dart
import 'package:firebase_performance/firebase_performance.dart';

// Custom trace
final trace = FirebasePerformance.instance.newTrace('payment_processing');
await trace.start();
trace.setMetric('processing_duration', 1500);
await trace.stop();

// Network monitoring
final metric = FirebasePerformance.instance
    .newHttpMetric('https://api.example.com/orders', HttpMethod.Post);
await metric.start();
// Make request
metric.setResponse(response);
await metric.stop();
```

### App Startup Time Target: <2 seconds
- **Measure:** Cold start + app ready to interaction
- **Components tracked:** System launch, Dart/Java startup, widget build time
- **Metrics:** `app_startup_ms`, `ttff_ms` (time to first frame)

### Screen Load Time Target: <1 second
- **Custom trace per screen:** `screen_{name}_load_time`
- **Track:** Network fetch, data parsing, UI render

---

## 3. Analytics

### Firebase Analytics

**React Native:**
```javascript
import analytics from '@react-native-firebase/analytics';

// Standard events
analytics().logEvent({
  name: 'purchase',
  parameters: {
    value: 99.99,
    currency: 'USD',
    items: [{ name: 'premium_subscription' }],
  },
});

// Event taxonomy: category_action
analytics().logEvent({
  name: 'home_feed_scroll',
  parameters: {
    scroll_depth: 5,
    session_duration_ms: 45000,
  },
});

// Set user properties
analytics().setUserId('user-123');
analytics().setUserProperties({
  subscription_tier: 'premium',
  cohort: 'early_adopter',
});
```

**Flutter:**
```dart
import 'package:firebase_analytics/firebase_analytics.dart';

// Track event
await FirebaseAnalytics.instance.logEvent(
  name: 'purchase',
  parameters: {
    'value': 99.99,
    'currency': 'USD',
  },
);

// Set user properties
await FirebaseAnalytics.instance.setUserId('user-123');
await FirebaseAnalytics.instance.setUserProperty(
  name: 'subscription_tier',
  value: 'premium',
);
```

### Event Taxonomy Best Practices
```
Category_Action: purchase_initiated, purchase_completed
Context properties: user_segment, ab_test_variant, feature_flag_state
```

### Retention Tracking
- **Day 1, 7, 30 retention:** Cohort analysis based on install date
- **Churn prediction:** Model users with no events in 7 days as churned

---

## 4. Logging

### React Native (Structured Logging)
```javascript
import { logger } from './utils/logger';

// Create logger instance
const log = {
  info: (msg, context) => console.log(`[INFO] ${msg}`, context),
  warn: (msg, context) => console.warn(`[WARN] ${msg}`, context),
  error: (msg, context) => console.error(`[ERROR] ${msg}`, context),
};

// Structured log pattern
log.info('User authentication', {
  userId: 'user-123',
  method: 'oauth',
  provider: 'google',
  duration_ms: 1250,
  timestamp: new Date().toISOString(),
});

// Remote logging
import RNFetchBlob from 'rn-fetch-blob';

const sendLogs = async (logs) => {
  await RNFetchBlob.fetch('POST', 'https://logs.example.com/api/logs', {},
    JSON.stringify({ logs, deviceId: getDeviceId() }));
};
```

### iOS (OSLog)
```swift
import os.log

let logger = Logger(subsystem: "com.example.app", category: "payment")

logger.info("Payment initiated: \(paymentId, privacy: .private(mask: .hash))")
logger.error("Payment failed: \(error.localizedDescription)")

// Log levels: debug, info, notice, warning, error, critical
logger.warning("High memory usage: \(memoryMB)MB")
```

### Android (Timber)
```kotlin
import timber.log.Timber

// Initialize
Timber.plant(DebugTree())
if (BuildConfig.DEBUG) {
  Timber.plant(CrashReportingTree()) // Remote logging
}

Timber.i("User signed in: %s", userId)
Timber.w("Low battery: %d%%", batteryPercent)
Timber.e(exception, "Payment processing failed")

// Custom tree for remote logging
class CrashReportingTree : Timber.Tree() {
  override fun log(priority: Int, tag: String?, message: String, t: Throwable?) {
    if (priority >= Log.ERROR) {
      sendToServer(message, t)
    }
  }
}
```

### Flutter (Logger)
```dart
import 'package:logger/logger.dart';

final logger = Logger(
  level: Level.debug,
  printer: PrettyPrinter(
    methodCount: 2,
    printEmojis: true,
  ),
);

logger.i('User authenticated: $userId');
logger.e('Network error', error: exception, stackTrace: st);
logger.w('Cache invalidated');
```

### What to Log vs NOT Log
```
DO LOG:
- User actions (login, purchase, feature use)
- Error conditions with context
- Performance metrics (API latency, load times)
- Feature flags and A/B test assignments

DO NOT LOG:
- Passwords, tokens, API keys
- Full payment card numbers
- Personal identification numbers
- Health/medical data
- Biometric data
```

---

## 5. Error Budgets & SLOs

### Mobile Error Budget Framework
```
Monthly Error Budget (99.5% availability):
- Total sessions: 1,000,000
- Allowed crashing sessions: 5,000 (0.5%)

Metrics to track:
1. Crash-free rate: >99.5% (target: 99.9%)
2. ANR rate: <0.5% of sessions
3. App startup time: <2 seconds (p95)
4. Frame drops: <5% (jank-free frames)
5. Network errors: <1% of API calls
```

### SLI/SLO/SLA Definitions
```
SLI (Service Level Indicator):
- (Sessions without crash) / Total sessions × 100

SLO (Service Level Objective):
- Maintain 99.5% crash-free rate monthly
- ANR incidents <1 per day
- API availability >99.9%

SLA (Service Level Agreement):
- Monthly credit if crash-free < 99%
- P99 startup time <3 seconds
```

### Alerting Thresholds
```
CRITICAL (Page immediately):
- Crash-free rate < 98% in current hour
- ANR rate > 2% in current hour
- 50%+ devices unable to authenticate

WARNING (Page within 30 min):
- Crash-free rate < 99% in current day
- API error rate > 5%
- Startup time > 3 seconds (p95)

INFO (Log to dashboard):
- Crash-free rate trend downward
- New top crash affects >1% of sessions
```

---

## 6. Feature Flags & Remote Config

### Firebase Remote Config

**React Native:**
```javascript
import remoteConfig from '@react-native-firebase/remote-config';

await remoteConfig().setConfigSettings({
  minimumFetchIntervalMillis: 3600000, // 1 hour
});

// Fetch and activate
await remoteConfig().fetchAndActivate();

// Read config
const premiumFeatureEnabled = remoteConfig().getBoolean('premium_features_enabled');
const apiEndpoint = remoteConfig().getString('api_endpoint');
const maxRetries = remoteConfig().getNumber('max_retries');

// Targeted rollout (percentage)
const rolloutPercent = remoteConfig().getNumber('new_checkout_rollout');
if (Math.random() * 100 < rolloutPercent) {
  showNewCheckout();
}

// Kill switch pattern
const isFeatureAvailable = remoteConfig().getBoolean('feature_payment_v2_enabled');
if (!isFeatureAvailable) {
  fallbackToLegacyPayment();
}
```

**Flutter:**
```dart
import 'package:firebase_remote_config/firebase_remote_config.dart';

final remoteConfig = FirebaseRemoteConfig.instance;
await remoteConfig.setConfigSettings(RemoteConfigSettings(
  fetchTimeout: const Duration(minutes: 1),
  minimumFetchInterval: const Duration(hours: 1),
));

await remoteConfig.ensureInitialized();
await remoteConfig.fetchAndActivate();

// Read values
bool isPremiumEnabled = remoteConfig.getBool('premium_features_enabled');
String apiEndpoint = remoteConfig.getString('api_endpoint');

// A/B test variant assignment
String variant = remoteConfig.getString('checkout_variant');
if (variant == 'new_ui') {
  showNewCheckout();
}
```

### LaunchDarkly

```javascript
// React Native
import * as LaunchDarkly from '@launchdarkly/react-native-client-sdk';

const ldClient = new LaunchDarkly.LDClient();
ldClient.init({
  mobileKey: 'mobile-key-xxx',
  context: {
    kind: 'user',
    key: 'user-123',
    custom: {
      subscription_tier: 'premium',
      cohort: 'early_adopter',
    },
  },
});

// Check flag
const newPaymentUI = ldClient.boolVariation('new-payment-ui', false);

// Track custom events for analytics
ldClient.track('payment_processed', null, 99.99);
```

### Gradual Rollout Pattern
```
Version 1.0.0: 0% rollout
Version 1.1.0: 10% rollout (day 1)
Version 1.1.0: 50% rollout (day 2)
Version 1.1.0: 100% rollout (day 3)

Monitor: Crash-free rate, ANR rate, API latency per variant
Rollback: If variant shows >10% increase in crashes
```

---

## 7. Alerting & On-Call

### PagerDuty Integration
```javascript
// Alert on high crash rate
const checkCrashRate = async () => {
  const crashRate = await getCrashRateLastHour();
  if (crashRate > 0.02) { // 2%
    await triggerPagerDutyAlert({
      severity: 'critical',
      title: 'High crash rate detected',
      service: 'mobile-app',
      details: { crashRate, affectedUsers: 50000 },
    });
  }
};

// Run every 5 minutes
setInterval(checkCrashRate, 5 * 60 * 1000);
```

### Escalation Policy
```
Level 1 (5 min): On-call engineer
Level 2 (10 min): Engineering lead
Level 3 (15 min): Mobile platform team lead

Escalation triggers:
- Crash-free < 98%
- 10,000+ affected users
- Payment flow unavailable
```

### Alert Fatigue Prevention
```
Rules:
1. Alert only on actionable metrics
2. Minimum 5-min detection window (avoid noise)
3. Group related alerts (e.g., all crash types)
4. Auto-resolve alerts when metric recovers
5. Require confirmation for non-critical alerts
```

### Runbook Template
```markdown
## Spike in Crash Rate (>2%)

**Detection:** PagerDuty alert from Firebase Crashlytics
**Impact:** {estimated users} affected

**Investigation:**
1. Check top 3 crashes: Crashlytics dashboard
2. Identify version: Which build introduced regression?
3. Root cause: Check code diff, third-party deps
4. User impact: Is it blocking functionality?

**Mitigation:**
1. Quick fix + release new version
2. OR: Use remote config kill switch to disable feature
3. OR: Rollback via App Store/Play Store

**Communication:**
- Post status in #incidents Slack
- Update affected customers within 30 minutes
```

---

## 8. User Feedback & Session Replay

### In-App Feedback Widget
```javascript
// React Native custom implementation
const FeedbackButton = () => {
  const [showFeedback, setShowFeedback] = useState(false);

  const submitFeedback = async (feedback, screenshot) => {
    const payload = {
      message: feedback,
      screenshot: screenshot,
      userId: getCurrentUserId(),
      appVersion: getAppVersion(),
      deviceModel: getDeviceModel(),
      osVersion: getOSVersion(),
      timestamp: new Date().toISOString(),
    };
    await api.post('/feedback', payload);
  };

  return (
    <>
      <TouchableOpacity onPress={() => setShowFeedback(true)}>
        <Text>Send Feedback</Text>
      </TouchableOpacity>
      {showFeedback && <FeedbackForm onSubmit={submitFeedback} />}
    </>
  );
};
```

### Shake-to-Report (React Native)
```javascript
import { accelerometer } from 'react-native-sensors';

const ShakeDetector = ({ onShake }) => {
  useEffect(() => {
    const subscription = accelerometer.subscribe(({ x, y, z }) => {
      const force = Math.sqrt(x * x + y * y + z * z);
      if (force > 50) { // Threshold for shake
        onShake();
      }
    });
    return () => subscription.unsubscribe();
  }, [onShake]);

  return null;
};
```

### Session Replay (FullStory)
```javascript
import { FullStory } from '@fullstory/react-native';

FullStory.init({
  orgId: 'org-id',
  useScreens: true,
});

// Tag sessions
FullStory.setUserVars({
  userId: 'user-123',
  displayName: 'John Doe',
  email: 'john@example.com',
});

// Redact sensitive data
FullStory.setSessionVars({
  'credit_card': FullStory.MASK_ALL,
  'password': FullStory.MASK_ALL,
});
```

### NPS Survey
```javascript
const NPSSurvey = ({ onComplete }) => {
  const [score, setScore] = useState(null);

  const handleSubmit = async () => {
    await api.post('/nps', {
      score,
      timestamp: new Date().toISOString(),
      userId: getCurrentUserId(),
      appVersion: getAppVersion(),
    });
    onComplete();
  };

  return (
    <View>
      <Text>How likely are you to recommend our app?</Text>
      <View style={{ flexDirection: 'row' }}>
        {[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(num => (
          <TouchableOpacity
            key={num}
            onPress={() => setScore(num)}
            style={[score === num && { backgroundColor: 'blue' }]}
          >
            <Text>{num}</Text>
          </TouchableOpacity>
        ))}
      </View>
      <TouchableOpacity onPress={handleSubmit}>
        <Text>Submit</Text>
      </TouchableOpacity>
    </View>
  );
};
```

---

## 9. Release Health Monitoring

### Staged Rollout Monitoring
```javascript
// Compare metrics between versions
const compareVersionMetrics = async (versionA, versionB) => {
  const metricsA = await getVersionMetrics(versionA);
  const metricsB = await getVersionMetrics(versionB);

  const comparison = {
    crashFreeRate: {
      [versionA]: metricsA.crashFreeRate,
      [versionB]: metricsB.crashFreeRate,
      regression: metricsB.crashFreeRate < metricsA.crashFreeRate * 0.99,
    },
    startupTime: {
      [versionA]: metricsA.startupTimeP95,
      [versionB]: metricsB.startupTimeP95,
      regression: metricsB.startupTimeP95 > metricsA.startupTimeP95 * 1.1,
    },
    anrRate: {
      [versionA]: metricsA.anrRate,
      [versionB]: metricsB.anrRate,
      regression: metricsB.anrRate > metricsA.anrRate * 1.5,
    },
  };

  return comparison;
};

// Rollback criteria
if (comparison.crashFreeRate.regression ||
    comparison.anrRate.regression) {
  await initiateRollback(versionB);
  await sendAlertToTeam('Rolled back version due to regression');
}
```

### Version Adoption Tracking
```
Track by App Store/Play Store:
- Active installs by version
- Update rate (days to 50%, 90%)
- Crash rate by version
- ANR rate by version

Dashboard metrics:
- 1.0.0: 45% installs, 98.5% crash-free
- 1.1.0: 50% installs, 98.2% crash-free (regression: -0.3%)
- 1.2.0 beta: 5% installs (staged rollout)
```

---

## 10. Privacy-Compliant Monitoring

### GDPR-Compliant Analytics
```javascript
// Consent management
const requestAnalyticsConsent = async () => {
  const consented = await showConsentPrompt(
    'Help us improve by sharing usage analytics'
  );

  if (consented) {
    analytics().setAnalyticsCollectionEnabled(true);
    crashlytics().setCrashlyticsCollectionEnabled(true);
  } else {
    analytics().setAnalyticsCollectionEnabled(false);
    crashlytics().setCrashlyticsCollectionEnabled(false);
  }

  // Store consent
  await preferences.set('analytics_consent', consented);
};

// On app start
useEffect(() => {
  const hasConsent = preferences.get('analytics_consent');
  if (hasConsent === null) {
    requestAnalyticsConsent();
  }
}, []);
```

### User Anonymization
```javascript
// Remove personally identifiable information
const anonymizeUser = async (userId) => {
  // Clear analytics user ID
  analytics().setUserId(null);

  // Remove user properties
  analytics().setUserProperties({
    email: null,
    name: null,
    phone: null,
  });

  // Mark as deleted in backend
  await api.post(`/users/${userId}/anonymize`);
};

// Data retention policy
const deleteOldLogs = async () => {
  // Keep only last 30 days of logs
  const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
  await db.logs.deleteWhere('timestamp < ?', [thirtyDaysAgo]);
};
```

### ATT Opt-In Tracking (iOS)
```swift
import AppTrackingTransparency

func requestTrackingPermission() {
  if #available(iOS 14, *) {
    ATTrackingManager.requestTrackingAuthorization { status in
      switch status {
      case .authorized:
        Analytics.setAnalyticsCollectionEnabled(true)
      case .denied, .restricted:
        Analytics.setAnalyticsCollectionEnabled(false)
      case .notDetermined:
        break
      @unknown default:
        break
      }
    }
  }
}

// Track ATT status in analytics
let attStatus = ATTrackingManager.trackingAuthorizationStatus
let statusString = attStatus == .authorized ? "allowed" : "denied"
Analytics.logEvent("att_status", parameters: ["value": statusString])
```

### Data Retention Policy
```
Analytics events: 12 months
Crash logs: 90 days
User activity logs: 30 days
Session recordings: 7 days
PII (email, names): 0 days (anonymize immediately)

Implement: Automated cleanup jobs, audit logs, GDPR deletion requests
```

---

## Quick Reference Checklist

- [ ] Crash reporting integrated (target >99.5% crash-free)
- [ ] Performance monitoring tracking startup time & screen load
- [ ] Analytics event taxonomy defined with user properties
- [ ] Structured logging with remote aggregation
- [ ] Error budget defined with alerting thresholds
- [ ] Feature flags for gradual rollouts and kill switches
- [ ] On-call alerts configured with runbooks
- [ ] User feedback & session replay enabled
- [ ] Release health monitoring with regression detection
- [ ] Privacy consent & data retention policies implemented
- [ ] ATT opt-in tracking (iOS) configured
- [ ] Monthly SLO reviews scheduled
