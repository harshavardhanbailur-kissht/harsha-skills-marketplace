# Deep Linking Reference Guide

Deep linking enables users to access specific content or screens within your app through URLs. This comprehensive guide covers implementation strategies across iOS, Android, React Native, and Flutter.

## Table of Contents

- [1. Universal Links (iOS)](#1-universal-links-ios)
- [2. App Links (Android)](#2-app-links-android)
- [3. React Native Deep Linking](#3-react-native-deep-linking)
- [4. Flutter Deep Linking](#4-flutter-deep-linking)
- [5. Deferred Deep Linking](#5-deferred-deep-linking)
- [6. QR Code Deep Links](#6-qr-code-deep-links)
- [7. Push Notification Deep Linking](#7-push-notification-deep-linking)
- [8. Navigation Architecture](#8-navigation-architecture)
- [9. Type-Safe Routing Patterns](#9-type-safe-routing-patterns)
- [10. Navigation State Persistence and Restoration](#10-navigation-state-persistence-and-restoration)
- [11. Attribution Tracking](#11-attribution-tracking)
- [12. Deep Link Testing and Validation Tools](#12-deep-link-testing-and-validation-tools)

## 1. Universal Links (iOS)

Universal Links allow iOS apps to open URLs directly without showing a browser. They're the preferred approach for iOS deep linking.

### AASA File Configuration

Create `apple-app-site-association` (AASA) file in `.well-known` directory:

```json
{
  "applinks": {
    "apps": [],
    "details": [
      {
        "appID": "TEAM_ID.com.example.myapp",
        "paths": [
          "/content/*",
          "/user/*",
          "/product/*"
        ]
      },
      {
        "appID": "TEAM_ID.com.example.myapp.staging",
        "paths": [
          "/beta/*"
        ]
      }
    ]
  },
  "webcredentials": {
    "apps": [
      "TEAM_ID.com.example.myapp"
    ]
  }
}
```

Host at: `https://yourdomain.com/.well-known/apple-app-site-association`

### Associated Domains Configuration

In Xcode, enable Associated Domains capability and add:

```swift
// Info.plist
<key>com.apple.developer.associated-domains</key>
<array>
  <string>applinks:yourdomain.com</string>
  <string>applinks:www.yourdomain.com</string>
  <string>webcredentials:yourdomain.com</string>
</array>
```

### SwiftUI Deep Link Handling

```swift
import SwiftUI

@main
struct MyApp: App {
  @State private var navigationPath = NavigationPath()

  var body: some Scene {
    WindowGroup {
      ContentView()
        .navigationDestination(for: DeepLink.self) { link in
          handleDeepLink(link)
        }
        .onOpenURL { url in
          if let deepLink = parseDeepLink(url) {
            navigationPath.append(deepLink)
          }
        }
    }
  }

  func parseDeepLink(_ url: URL) -> DeepLink? {
    guard let components = URLComponents(url: url, resolvingAgainstBaseURL: true) else {
      return nil
    }

    let pathSegments = components.path
      .split(separator: "/")
      .map(String.init)

    switch (pathSegments.first, pathSegments.dropFirst().first) {
    case ("content", let contentID?):
      return .content(id: contentID)
    case ("user", let userID?):
      return .user(id: userID)
    case ("product", let productID?):
      return .product(id: productID)
    case ("search", _):
      let query = components.queryItems?
        .first(where: { $0.name == "q" })?
        .value ?? ""
      return .search(query: query)
    default:
      return nil
    }
  }

  @ViewBuilder
  func handleDeepLink(_ link: DeepLink) -> some View {
    switch link {
    case .content(let id):
      ContentDetailView(contentID: id)
    case .user(let id):
      UserProfileView(userID: id)
    case .product(let id):
      ProductView(productID: id)
    case .search(let query):
      SearchResultsView(query: query)
    }
  }
}

enum DeepLink: Hashable {
  case content(id: String)
  case user(id: String)
  case product(id: String)
  case search(query: String)
}
```

## 2. App Links (Android)

App Links are Android's equivalent to Universal Links, providing verified deep linking.

### Intent Filters Configuration

```xml
<!-- AndroidManifest.xml -->
<activity
  android:name=".MainActivity"
  android:exported="true">

  <intent-filter android:autoVerify="true">
    <action android:name="android.intent.action.VIEW" />
    <category android:name="android.intent.category.DEFAULT" />
    <category android:name="android.intent.category.BROWSABLE" />

    <data
      android:scheme="https"
      android:host="yourdomain.com"
      android:pathPrefix="/content/" />
    <data
      android:scheme="https"
      android:host="yourdomain.com"
      android:pathPrefix="/user/" />
    <data
      android:scheme="https"
      android:host="yourdomain.com"
      android:pathPrefix="/product/" />
  </intent-filter>

  <!-- Custom scheme fallback -->
  <intent-filter>
    <action android:name="android.intent.action.VIEW" />
    <category android:name="android.intent.category.DEFAULT" />
    <category android:name="android.intent.category.BROWSABLE" />

    <data android:scheme="myapp" />
  </intent-filter>
</activity>
```

### Digital Asset Links Configuration

Create `.well-known/assetlinks.json`:

```json
[
  {
    "relation": ["delegate_permission/common.handle_all_urls"],
    "target": {
      "namespace": "android_app",
      "package_name": "com.example.myapp",
      "sha256_cert_fingerprints": [
        "AA:BB:CC:DD:EE:FF:00:11:22:33:44:55:66:77:88:99:AA:BB:CC:DD:EE:FF:00:11:22:33:44:55:66:77:88:99"
      ]
    }
  }
]
```

Get SHA256 fingerprint:
```bash
keytool -list -v -keystore ~/.android/debug.keystore -alias androiddebugkey -storepass android -keypass android
```

### Android Deep Link Handling

```kotlin
// MainActivity.kt
import android.content.Intent
import android.net.Uri
import androidx.activity.compose.setContent
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {
  override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)

    setContent {
      MyApp()
    }

    handleDeepLink(intent)
  }

  override fun onNewIntent(intent: Intent) {
    super.onNewIntent(intent)
    handleDeepLink(intent)
  }

  private fun handleDeepLink(intent: Intent) {
    val deepLink = intent.data
    deepLink?.let {
      val pathSegments = it.pathSegments
      when {
        pathSegments.firstOrNull() == "content" && pathSegments.size > 1 -> {
          val contentId = pathSegments[1]
          navigateToContent(contentId)
        }
        pathSegments.firstOrNull() == "user" && pathSegments.size > 1 -> {
          val userId = pathSegments[1]
          navigateToUser(userId)
        }
        pathSegments.firstOrNull() == "product" && pathSegments.size > 1 -> {
          val productId = pathSegments[1]
          navigateToProduct(productId)
        }
        it.scheme == "myapp" -> {
          val path = it.host
          navigateByCustomScheme(path)
        }
      }
    }
  }

  private fun navigateToContent(contentId: String) {
    // Navigation logic
  }

  private fun navigateToUser(userId: String) {
    // Navigation logic
  }

  private fun navigateToProduct(productId: String) {
    // Navigation logic
  }

  private fun navigateByCustomScheme(path: String) {
    // Custom scheme handling
  }
}
```

## 3. React Native Deep Linking

### React Navigation Configuration

```typescript
// LinkingConfiguration.ts
import * as Linking from 'expo-linking';

const prefix = Linking.createURL('/');

const linking = {
  prefixes: [
    prefix,
    'myapp://',
    'https://yourdomain.com/',
  ],
  config: {
    screens: {
      ContentDetail: 'content/:contentId',
      UserProfile: 'user/:userId',
      ProductDetail: 'product/:productId',
      Search: {
        path: 'search',
        parse: {
          query: (query: string) => decodeURIComponent(query ?? ''),
        },
      },
      NotFound: '*',
    },
  },
};

export default linking;
```

### Navigation Setup

```typescript
// Navigation.tsx
import React, { useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import * as Linking from 'expo-linking';
import linking from './LinkingConfiguration';

const Stack = createNativeStackNavigator();

export function RootNavigator() {
  const navigationRef = React.useRef(null);

  useEffect(() => {
    const unsubscribe = Linking.addEventListener('url', ({ url }) => {
      const state = navigationRef.current?.getRootState();
      const params = url.replace(/.*?\/\/, '').split('/');

      navigationRef.current?.navigate('ContentDetail', {
        contentId: params[1],
      });
    });

    return () => unsubscribe.remove();
  }, []);

  return (
    <NavigationContainer linking={linking} ref={navigationRef} fallback={<LoadingScreen />}>
      <Stack.Navigator>
        <Stack.Screen name="Home" component={HomeScreen} />
        <Stack.Screen name="ContentDetail" component={ContentDetailScreen} />
        <Stack.Screen name="UserProfile" component={UserProfileScreen} />
        <Stack.Screen name="ProductDetail" component={ProductDetailScreen} />
        <Stack.Screen name="Search" component={SearchScreen} />
        <Stack.Screen name="NotFound" component={NotFoundScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
```

### Expo Router Deep Linking

```typescript
// app.json
{
  "expo": {
    "plugins": [
      [
        "expo-router",
        {
          "origin": "https://yourdomain.com",
          "prefixes": [
            "myapp://",
            "exp+myapp://"
          ]
        }
      ]
    ],
    "scheme": "myapp"
  }
}
```

```typescript
// app/_layout.tsx
import { Stack, useSegments } from 'expo-router';
import { useEffect } from 'react';

export default function RootLayout() {
  const segments = useSegments();

  useEffect(() => {
    // Deep link routing with Expo Router is automatic
    // Router reads the URL and navigates based on file structure
  }, [segments]);

  return (
    <Stack>
      <Stack.Screen name="index" />
      <Stack.Screen name="content/[id]" />
      <Stack.Screen name="user/[id]" />
      <Stack.Screen name="product/[id]" />
    </Stack>
  );
}
```

## 4. Flutter Deep Linking

### GoRouter Configuration

```dart
// lib/router/router.dart
import 'package:go_router/go_router.dart';

final router = GoRouter(
  routes: [
    GoRoute(
      path: '/',
      builder: (context, state) => const HomeScreen(),
      routes: [
        GoRoute(
          path: 'content/:contentId',
          builder: (context, state) => ContentDetailScreen(
            contentId: state.pathParameters['contentId']!,
          ),
        ),
        GoRoute(
          path: 'user/:userId',
          builder: (context, state) => UserProfileScreen(
            userId: state.pathParameters['userId']!,
          ),
        ),
        GoRoute(
          path: 'product/:productId',
          builder: (context, state) => ProductDetailScreen(
            productId: state.pathParameters['productId']!,
          ),
        ),
        GoRoute(
          path: 'search',
          builder: (context, state) {
            final query = state.uri.queryParameters['q'] ?? '';
            return SearchScreen(query: query);
          },
        ),
      ],
    ),
  ],
  initialLocation: '/',
);
```

### App Links and Uni Links

```dart
// pubspec.yaml
dependencies:
  app_links: ^3.4.1
  uni_links: ^0.0.10

// AndroidManifest.xml
<intent-filter android:autoVerify="true">
  <action android:name="android.intent.action.VIEW" />
  <category android:name="android.intent.category.DEFAULT" />
  <category android:name="android.intent.category.BROWSABLE" />

  <data android:scheme="https" android:host="yourdomain.com" android:pathPrefix="/content/" />
  <data android:scheme="https" android:host="yourdomain.com" android:pathPrefix="/user/" />
  <data android:scheme="https" android:host="yourdomain.com" android:pathPrefix="/product/" />
</intent-filter>

// lib/main.dart
import 'package:app_links/app_links.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  final appLinks = AppLinks();

  appLinks.uriLinkStream.listen((uri) {
    router.go(uri.path, extra: uri.queryParameters);
  });

  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      routerConfig: router,
      title: 'Deep Link App',
    );
  }
}
```

## 5. Deferred Deep Linking

Deferred deep linking works even when the app isn't installed by installing first then navigating.

### Branch.io Implementation

```typescript
// React Native with Branch.io
import { BranchEvent, BranchSubscriber } from 'react-native-branch';

const initBranch = async () => {
  // Enable deep link tracking
  BranchSubscriber.subscribe({
    onOpenStart: ({ cachedInitialEvent }) => {
      console.log('Branch subscriber: onOpenStart', cachedInitialEvent);
    },
    onOpenComplete: () => {
      console.log('Branch subscriber: onOpenComplete');
    },
    onError: (error) => {
      console.log('Branch subscriber error:', error);
    },
  });
};

// Create deep link
const createDeepLink = async () => {
  const branchUniversalObject = await BranchUniversalObject.create({
    canonicalIdentifier: 'content/123',
    title: 'Check out this content',
    contentDescription: 'Interesting content for you',
    contentImageUrl: 'https://example.com/image.jpg',
    contentMetadata: {
      contentSchema: 'article',
      customKey: 'customValue',
    },
  });

  const linkProperties = {
    alias: 'content-123',
    channel: 'facebook',
    feature: 'sharing',
    campaign: 'summer-sale',
    tags: ['promotion'],
  };

  const { url } = await branchUniversalObject.generateShortUrl(
    linkProperties
  );

  return url;
};
```

### AppsFlyer Implementation

```typescript
// React Native with AppsFlyer
import appsFlyer from 'react-native-appsflyer';

const initAppsFlyer = () => {
  appsFlyer.initSdk(
    {
      devKey: 'YOUR_DEV_KEY',
      isDebug: true,
      appId: 'YOUR_APP_ID',
      onDeepLinkListener: true,
    },
    (result) => {
      console.log('AppsFlyer init result:', result);
    },
    (error) => {
      console.log('AppsFlyer init error:', error);
    }
  );

  // Handle deep link
  appsFlyer.onDeepLink((result) => {
    if (result?.deepLinkStatus === 'Limit Reached') {
      console.log('Deferred deep link limit reached');
      return;
    }

    const { deepLink } = result;
    const mediaSource = result?.mediaSource;

    if (deepLink && mediaSource) {
      handleDeferredDeepLink(deepLink);
    }
  });
};

const handleDeferredDeepLink = (deepLink: string) => {
  // Parse and navigate based on deferred link
  const url = new URL(deepLink);
  const contentId = url.searchParams.get('content_id');
  // Navigate to content
};

// Track user for attribution
const trackEvent = () => {
  appsFlyer.logEvent(
    'purchase',
    {
      af_content_id: 'content_123',
      af_content_type: 'article',
      af_value: 49.99,
      af_currency: 'USD',
    },
    (result) => {
      console.log('Event tracked:', result);
    },
    (error) => {
      console.log('Event tracking error:', error);
    }
  );
};
```

## 6. QR Code Deep Links

```typescript
// React Native QR code deep linking
import { CameraView, useCameraPermissions } from 'expo-camera';
import QRCode from 'react-native-qrcode-svg';

export function QRScannerScreen() {
  const [permission, requestPermission] = useCameraPermissions();

  const handleBarcodeScanned = ({ type, data }) => {
    if (type === 'qr') {
      // data contains the deep link URL
      Linking.openURL(data).catch((err) => {
        console.log('Error opening URL:', err);
      });
    }
  };

  return (
    <CameraView
      onBarcodeScanned={handleBarcodeScanned}
      barcodeScannerSettings={{
        barcodeTypes: ['qr'],
      }}
    />
  );
}

export function QRGeneratorScreen({ contentId }: { contentId: string }) {
  const deepLinkUrl = `https://yourdomain.com/content/${contentId}`;

  return (
    <QRCode
      value={deepLinkUrl}
      size={300}
      color="black"
      backgroundColor="white"
    />
  );
}
```

## 7. Push Notification Deep Linking

```typescript
// Firebase Cloud Messaging with deep links
import messaging from '@react-native-firebase/messaging';
import { useNavigation } from '@react-navigation/native';

export function usePushNotificationListener() {
  const navigation = useNavigation();

  useEffect(() => {
    // Handle notification when app is in foreground
    const unsubscribe = messaging().onMessage(async (remoteMessage) => {
      const deepLink = remoteMessage.data?.deepLink;
      if (deepLink) {
        navigation.navigate('ContentDetail', { contentId: deepLink });
      }
    });

    // Handle notification when app is opened from background
    messaging().onNotificationOpenedApp((remoteMessage) => {
      const deepLink = remoteMessage?.data?.deepLink;
      if (deepLink) {
        navigation.navigate('ContentDetail', { contentId: deepLink });
      }
    });

    // Check if app was opened from terminated state
    messaging()
      .getInitialNotification()
      .then((remoteMessage) => {
        if (remoteMessage?.data?.deepLink) {
          navigation.navigate('ContentDetail', {
            contentId: remoteMessage.data.deepLink,
          });
        }
      });

    return unsubscribe;
  }, [navigation]);
}

// Send notification with deep link via Firebase Admin SDK
admin.messaging().send({
  notification: {
    title: 'Check out this content',
    body: 'You might like this article',
  },
  data: {
    deepLink: 'myapp://content/123',
    contentId: '123',
    source: 'notification',
  },
  token: userFcmToken,
});
```

## 8. Navigation Architecture

### Stack Navigator Pattern

```typescript
// Stack-based navigation
const Stack = createNativeStackNavigator();

export function ContentStack() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: true,
        gestureEnabled: true,
      }}
    >
      <Stack.Screen
        name="ContentList"
        component={ContentListScreen}
        options={{ title: 'Content' }}
      />
      <Stack.Screen
        name="ContentDetail"
        component={ContentDetailScreen}
        options={({ route }) => ({
          title: route.params?.title || 'Content Detail',
        })}
      />
      <Stack.Screen
        name="ContentEdit"
        component={ContentEditScreen}
        options={{
          title: 'Edit Content',
          presentation: 'modal',
        }}
      />
    </Stack.Navigator>
  );
}
```

### Tab Navigator with Stack

```typescript
const Tab = createBottomTabNavigator();
const HomeStack = createNativeStackNavigator();
const ProfileStack = createNativeStackNavigator();

export function HomeStackNavigator() {
  return (
    <HomeStack.Navigator>
      <HomeStack.Screen name="HomeList" component={HomeScreen} />
      <HomeStack.Screen name="ContentDetail" component={ContentDetailScreen} />
    </HomeStack.Navigator>
  );
}

export function ProfileStackNavigator() {
  return (
    <ProfileStack.Navigator>
      <ProfileStack.Screen name="ProfileList" component={ProfileScreen} />
      <ProfileStack.Screen name="Settings" component={SettingsScreen} />
    </ProfileStack.Navigator>
  );
}

export function RootNavigator() {
  return (
    <Tab.Navigator>
      <Tab.Screen
        name="Home"
        component={HomeStackNavigator}
        options={{ tabBarLabel: 'Home' }}
      />
      <Tab.Screen
        name="Profile"
        component={ProfileStackNavigator}
        options={{ tabBarLabel: 'Profile' }}
      />
    </Tab.Navigator>
  );
}
```

### Nested Navigation with Modals

```typescript
const RootStack = createNativeStackNavigator();
const AppStack = createNativeStackNavigator();

export function AppNavigator() {
  return (
    <AppStack.Navigator screenOptions={{ headerShown: false }}>
      <AppStack.Screen name="Main" component={MainTabs} />
      <AppStack.Group screenOptions={{ presentation: 'modal' }}>
        <AppStack.Screen
          name="FullScreenModal"
          component={FullScreenModalScreen}
        />
        <AppStack.Screen
          name="DetailModal"
          component={DetailModalScreen}
        />
      </AppStack.Group>
    </AppStack.Navigator>
  );
}

export function RootNavigator() {
  const [isSignedIn, setIsSignedIn] = React.useState(false);

  return (
    <RootStack.Navigator screenOptions={{ headerShown: false }}>
      {isSignedIn ? (
        <RootStack.Screen
          name="App"
          component={AppNavigator}
        />
      ) : (
        <RootStack.Screen
          name="Auth"
          component={AuthNavigator}
        />
      )}
    </RootStack.Navigator>
  );
}
```

## 9. Type-Safe Routing Patterns

```typescript
// Strongly-typed routes
type RootStackParamList = {
  Home: undefined;
  ContentDetail: { contentId: string; title?: string };
  UserProfile: { userId: string };
  ProductDetail: { productId: string; category?: string };
  Search: { query: string };
};

declare global {
  namespace ReactNavigation {
    interface RootParamList extends RootStackParamList {}
  }
}

// Type-safe navigation
export function navigateToContent(
  navigation: NavigationProp<RootStackParamList>,
  contentId: string
) {
  navigation.navigate('ContentDetail', { contentId });
}

// Type-safe route params in screen component
interface ContentDetailScreenProps {
  route: RouteProp<RootStackParamList, 'ContentDetail'>;
}

export function ContentDetailScreen({ route }: ContentDetailScreenProps) {
  const { contentId, title } = route.params;

  return <Text>Content {contentId}: {title}</Text>;
}

// Deep link type validation
function parseAndValidateDeepLink(url: string): RootStackParamList[keyof RootStackParamList] | null {
  const parsed = new URL(url);
  const pathSegments = parsed.pathname.split('/').filter(Boolean);

  if (pathSegments[0] === 'content' && pathSegments[1]) {
    return {
      contentId: pathSegments[1],
      title: parsed.searchParams.get('title') || undefined,
    } as RootStackParamList['ContentDetail'];
  }

  return null;
}
```

## 10. Navigation State Persistence and Restoration

```typescript
// Persist and restore navigation state
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as SecureStore from 'expo-secure-store';

const PERSISTENCE_KEY = 'NAVIGATION_STATE';

export function NavigationPersistence() {
  const navigationRef = React.useRef();
  const [isReady, setIsReady] = React.useState(false);
  const [initialState, setInitialState] = React.useState();

  // Restore saved state
  React.useEffect(() => {
    const restoreState = async () => {
      try {
        const savedState = await AsyncStorage.getItem(PERSISTENCE_KEY);
        const initialRoute = savedState != null ? JSON.parse(savedState) : undefined;

        setInitialState(initialRoute);
      } finally {
        setIsReady(true);
      }
    };

    if (!isReady) {
      restoreState();
    }
  }, [isReady]);

  // Save state on navigation
  const onStateChange = async (state: NavigationState) => {
    try {
      await AsyncStorage.setItem(PERSISTENCE_KEY, JSON.stringify(state));
    } catch (error) {
      console.log('Failed to persist state:', error);
    }
  };

  if (!isReady) {
    return <SplashScreen />;
  }

  return (
    <NavigationContainer
      ref={navigationRef}
      initialState={initialState}
      onStateChange={onStateChange}
      linking={linking}
    >
      <RootNavigator />
    </NavigationContainer>
  );
}

// Handle app state changes for restoration
export function useAppStateListener(navigationRef: NavigationContainerRef) {
  const appState = React.useRef(AppState.currentState);

  React.useEffect(() => {
    const subscription = AppState.addEventListener('change', handleAppStateChange);

    return () => {
      subscription.remove();
    };

    function handleAppStateChange(nextAppState: AppStateStatus) {
      if (appState.current.match(/inactive|background/) && nextAppState === 'active') {
        // App has come to foreground
        // Restore state if necessary
      }

      appState.current = nextAppState;
    }
  }, [navigationRef]);
}
```

## 11. Attribution Tracking

```typescript
// Track deep link attribution
interface DeepLinkAttribution {
  source: string;
  campaign: string;
  medium: string;
  content: string;
  term: string;
  timestamp: number;
}

export async function trackDeepLinkAttribution(
  url: string,
  analyticsService: AnalyticsService
) {
  const parsed = new URL(url);
  const utm = {
    source: parsed.searchParams.get('utm_source') || 'direct',
    campaign: parsed.searchParams.get('utm_campaign') || 'organic',
    medium: parsed.searchParams.get('utm_medium') || 'deep_link',
    content: parsed.searchParams.get('utm_content') || '',
    term: parsed.searchParams.get('utm_term') || '',
  };

  const attribution: DeepLinkAttribution = {
    ...utm,
    timestamp: Date.now(),
  };

  // Store in persistent storage
  await AsyncStorage.setItem(
    'DEEP_LINK_ATTRIBUTION',
    JSON.stringify(attribution)
  );

  // Send to analytics
  analyticsService.trackEvent('deep_link_opened', {
    ...utm,
    screen: url.split('/')[1],
  });
}

// Firebase Analytics integration
export function trackDeepLinkWithFirebase(url: string) {
  const parsed = new URL(url);

  firebase.analytics().logEvent('app_open', {
    source: parsed.searchParams.get('utm_source'),
    campaign: parsed.searchParams.get('utm_campaign'),
    deep_link_url: url,
  });

  // Track content view
  if (url.includes('/content/')) {
    const contentId = url.split('/').pop();
    firebase.analytics().logEvent('view_item', {
      items: [
        {
          item_id: contentId,
          item_name: 'content',
        },
      ],
    });
  }
}
```

## 12. Deep Link Testing and Validation Tools

```bash
# iOS - Test Universal Links
xcrun simctl openurl booted "https://yourdomain.com/content/123"

# Android - Test App Links
adb shell am start -a android.intent.action.VIEW \
  -d "https://yourdomain.com/content/123" \
  com.example.myapp

# Custom scheme testing
adb shell am start -a android.intent.action.VIEW \
  -d "myapp://content/123"

# Verify AASA file (iOS)
curl https://yourdomain.com/.well-known/apple-app-site-association

# Verify assetlinks.json (Android)
curl https://yourdomain.com/.well-known/assetlinks.json
```

### Deep Link Testing Framework

```typescript
// Comprehensive deep link testing
import { render } from '@testing-library/react-native';

describe('Deep Linking', () => {
  it('should navigate to content detail', async () => {
    const { getByText } = render(<RootNavigator />);

    const url = 'myapp://content/123';
    await Linking.openURL(url);

    expect(getByText(/content detail/i)).toBeTruthy();
  });

  it('should parse deep link with query parameters', () => {
    const url = 'https://yourdomain.com/search?q=test';
    const deepLink = parseDeepLink(url);

    expect(deepLink).toEqual({
      type: 'search',
      query: 'test',
    });
  });

  it('should handle invalid deep links', () => {
    const url = 'myapp://invalid';
    const deepLink = parseDeepLink(url);

    expect(deepLink).toBeNull();
  });

  it('should restore navigation state', async () => {
    await AsyncStorage.setItem(
      'NAVIGATION_STATE',
      JSON.stringify({ routes: [{ name: 'ContentDetail' }] })
    );

    const { getByText } = render(<NavigationPersistence />);

    // Verify state was restored
    expect(getByText(/content detail/i)).toBeTruthy();
  });
});

// Deep link validation utility
export function validateDeepLink(url: string): boolean {
  try {
    const parsed = new URL(url);
    const validSchemes = ['https', 'myapp'];
    const validHosts = ['yourdomain.com', 'www.yourdomain.com'];

    if (!validSchemes.includes(parsed.protocol.replace(':', ''))) {
      return false;
    }

    if (parsed.protocol === 'https:' && !validHosts.includes(parsed.host)) {
      return false;
    }

    return true;
  } catch {
    return false;
  }
}
```

---

**Key Takeaways:**

- Use Universal Links (iOS) and App Links (Android) for verified deep linking
- Implement deferred deep linking for uninstalled app scenarios with Branch.io or AppsFlyer
- Type-safe routing prevents navigation errors
- Persist navigation state for better UX
- Track attribution for marketing analytics
- Test deep links thoroughly across platforms
- Handle both cold start and warm app scenarios
