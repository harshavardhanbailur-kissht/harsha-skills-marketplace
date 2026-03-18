# Hybrid Apps and PWAs: Comprehensive Reference Guide

A production-grade reference for building cross-platform mobile applications using hybrid frameworks (Capacitor, Ionic, .NET MAUI, Tauri) and Progressive Web Apps. This guide covers architecture, implementation patterns, and decision matrices for modern mobile development.

## Table of Contents

- [Capacitor](#capacitor)
- [Ionic Framework](#ionic-framework)
- [Progressive Web Apps (PWAs)](#progressive-web-apps-pwas)
- [WebView Integration](#webview-integration)
- [.NET MAUI](#net-maui)
- [Tauri Mobile v2](#tauri-mobile-v2)
- [Decision Matrix](#decision-matrix)
- [Production Checklist](#production-checklist)
- [Resources and References](#resources-and-references)

## Capacitor

### Architecture Overview

Capacitor is a bridge layer between web code (HTML/CSS/JavaScript) and native iOS/Android APIs. It uses WKWebView on iOS and Android WebView as the container, with a bidirectional JavaScript bridge for native communication.

**Core Architecture:**
```
┌─────────────────────┐
│   Web Application   │
│  (HTML/CSS/JS)      │
├─────────────────────┤
│  Capacitor JS API   │
├─────────────────────┤
│   Native Bridge     │
│  (IPC via postMsg)  │
├─────────────────────┤
│  Native Plugins     │
│ (Swift/Kotlin code) │
├─────────────────────┤
│   Device Hardware   │
└─────────────────────┘
```

### Project Setup

**Installation:**
```bash
# Create new Capacitor project
npm create @capacitor/app@latest -- --appName "MyApp" --appId "com.example.myapp"

# Or add to existing web project
npm install @capacitor/core @capacitor/cli
npx cap init MyApp com.example.myapp

# Add platforms
npx cap add ios
npx cap add android
```

**Configuration (capacitor.config.ts):**
```typescript
import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.example.myapp',
  appName: 'MyApp',
  webDir: 'dist',
  plugins: {
    SplashScreen: {
      launchShowDuration: 0,
    },
    PushNotifications: {
      presentationOptions: ['alert', 'sound', 'badge'],
    },
  },
  server: {
    url: 'http://192.168.1.100:3000', // Dev server
    cleartext: true, // Allow HTTP in development
  },
};

export default config;
```

### Native Plugin System

**Plugin Architecture:**

Plugins are npm packages that implement native functionality through a well-defined interface.

```typescript
// MyPlugin.ts - Web-facing interface
import { registerPlugin } from '@capacitor/core';

export interface MyPluginPlugin {
  echo(options: { value: string }): Promise<{ value: string }>;
  getDeviceId(): Promise<{ id: string }>;
}

export const MyPlugin = registerPlugin<MyPluginPlugin>('MyPlugin');
```

**Using Built-in Plugins:**

```typescript
import { Camera, CameraResultType } from '@capacitor/camera';
import { Filesystem, Directory, Encoding } from '@capacitor/filesystem';
import { Haptics } from '@capacitor/haptics';
import { App } from '@capacitor/app';
import { LocalNotifications } from '@capacitor/local-notifications';

// Camera
async function takePhoto() {
  const image = await Camera.getPhoto({
    quality: 90,
    allowEditing: false,
    resultType: CameraResultType.Uri,
  });
  return image.webPath;
}

// Filesystem
async function saveFile(content: string) {
  await Filesystem.writeFile({
    path: 'documents/myfile.txt',
    data: content,
    directory: Directory.Documents,
    encoding: Encoding.UTF8,
  });
}

// Haptics
async function vibrateDevice() {
  await Haptics.impact({ style: 'Medium' });
}

// App Info
const appInfo = await App.getInfo();
console.log(`Version: ${appInfo.version}`);

// Local Notifications
async function scheduleNotification() {
  await LocalNotifications.schedule({
    notifications: [
      {
        title: 'Meeting Reminder',
        body: 'You have a meeting in 5 minutes',
        id: 1,
        schedule: { at: new Date(Date.now() + 1000 * 60 * 5) },
      },
    ],
  });
}
```

### Creating Custom Plugins

**iOS Plugin (Swift):**

```swift
// MyPlugin.swift
import Capacitor

@objc(MyPlugin)
public class MyPlugin: CAPPlugin {
  @objc func echo(_ call: CAPPluginCall) {
    let value = call.getString("value") ?? ""
    call.resolve(["value": value])
  }

  @objc func getDeviceInfo(_ call: CAPPluginCall) {
    let model = UIDevice.current.model
    let version = UIDevice.current.systemVersion
    call.resolve([
      "model": model,
      "version": version
    ])
  }
}
```

**Android Plugin (Kotlin):**

```kotlin
// MyPlugin.kt
package com.example.myplugin

import com.getcapacitor.JSObject
import com.getcapacitor.Plugin
import com.getcapacitor.PluginCall
import com.getcapacitor.PluginMethod
import com.getcapacitor.annotation.CapacitorPlugin

@CapacitorPlugin(name = "MyPlugin")
class MyPlugin : Plugin() {
  @PluginMethod
  fun echo(call: PluginCall) {
    val value = call.getString("value", "")
    val result = JSObject()
    result.put("value", value)
    call.resolve(result)
  }

  @PluginMethod
  fun getDeviceInfo(call: PluginCall) {
    val result = JSObject()
    result.put("model", android.os.Build.MODEL)
    result.put("version", android.os.Build.VERSION.SDK_INT)
    call.resolve(result)
  }
}
```

### Platform-Specific Code

**Conditional Compilation:**

```typescript
import { Capacitor } from '@capacitor/core';

async function getPlatformData() {
  const platform = Capacitor.getPlatform(); // 'ios' | 'android' | 'web'

  if (platform === 'ios') {
    // iOS-specific implementation
    return await getIOSSpecificData();
  } else if (platform === 'android') {
    // Android-specific implementation
    return await getAndroidSpecificData();
  } else {
    // Web fallback
    return await getWebData();
  }
}

// Or use the isNativePlatform helper
if (Capacitor.isNativePlatform()) {
  // Native-only code
}
```

### Live Reload

**Development Server:**

```bash
# Terminal 1: Run web app dev server
npm run dev

# Terminal 2: Sync and run on device with live reload
npx cap run ios --livereload --external
npx cap run android --livereload --external
```

**Configuration:**

```bash
# Update capacitor.config.ts with dev server
server: {
  url: 'http://192.168.1.100:3000',
  cleartext: true,
},
```

### Deep Linking

**Configuration (capacitor.config.ts):**

```typescript
plugins: {
  CapacitorHttp: {
    enabled: true,
  },
},
server: {
  androidScheme: 'https',
},
```

**Implementation:**

```typescript
import { App } from '@capacitor/app';

// Listen for deep links
App.addListener('appUrlOpen', (data: any) => {
  const slug = data.url.split('.app').pop();
  if (slug) {
    navigateTo(slug);
  }
});

// Handle app launch URL
const url = await App.getLaunchUrl();
if (url?.url) {
  // Route based on URL
}
```

**Native Configuration (Info.plist for iOS):**

```xml
<key>CFBundleURLTypes</key>
<array>
  <dict>
    <key>CFBundleURLName</key>
    <string>com.example.myapp</string>
    <key>CFBundleURLSchemes</key>
    <array>
      <string>myapp</string>
    </array>
  </dict>
</array>
```

### Push Notifications

**Setup:**

```typescript
import { PushNotifications } from '@capacitor/push-notifications';

async function setupPushNotifications() {
  // Request permission
  let permStatus = await PushNotifications.checkPermissions();
  if (permStatus.receive === 'prompt') {
    permStatus = await PushNotifications.requestPermissions();
  }

  if (permStatus.receive !== 'granted') {
    throw new Error('Push notifications permission denied');
  }

  // Register for push
  await PushNotifications.register();

  // Listen for registration token
  PushNotifications.addListener('registration', (token: any) => {
    console.log('Push token:', token.value);
    // Send token to backend
  });

  // Handle incoming notifications
  PushNotifications.addListener('pushNotificationReceived', (notification: any) => {
    console.log('Notification received:', notification);
  });

  // Handle tap on notification
  PushNotifications.addListener('pushNotificationActionPerformed', (notification: any) => {
    const data = notification.notification.data;
    navigateTo(data.route);
  });
}
```

### Status Bar and Splash Screen

```typescript
import { StatusBar, Style } from '@capacitor/status-bar';
import { SplashScreen } from '@capacitor/splash-screen';

// Hide splash screen when app is ready
async function initializeApp() {
  await SplashScreen.hide();

  // Configure status bar
  await StatusBar.setStyle({ style: Style.Dark });
  await StatusBar.setBackgroundColor({ color: '#007AFF' });
}
```

### Capacitor vs Cordova

**Key Differences:**

| Feature | Capacitor | Cordova |
|---------|-----------|---------|
| Plugin System | Modern npm-based | Legacy |
| Modern Framework Support | Native React/Vue/Angular | Limited |
| Type Safety | Full TypeScript support | JavaScript-focused |
| Live Reload | Built-in | External tools |
| Dev Experience | Excellent | Dated |
| Performance | Native WebView | Native WebView |
| Migration Path | From Cordova | N/A |

**Migration from Cordova:**

```bash
# Install Capacitor in Cordova project
npm install @capacitor/core @capacitor/cli

# Initialize
npx cap init

# Add platforms (will read from Cordova config)
npx cap add ios
npx cap add android

# Migrate plugins (automated tool)
npx cap plugin add cordova-plugin-name

# Copy www to web directory
cp -r www/* web/
```

---

## Ionic Framework

### Overview

Ionic is a UI component library and SDK built on Capacitor, providing ready-made components optimized for mobile, with responsive design and platform-adaptive behavior.

### Core Components

**Header and Navigation:**

```typescript
import { IonHeader, IonToolbar, IonTitle, IonContent } from '@ionic/react';

function App() {
  return (
    <IonApp>
      <IonHeader>
        <IonToolbar color="primary">
          <IonTitle>My App</IonTitle>
        </IonToolbar>
      </IonHeader>
      <IonContent fullscreen>
        <div className="ion-padding">
          <h1>Welcome!</h1>
        </div>
      </IonContent>
    </IonApp>
  );
}
```

**List and Card Components:**

```typescript
import {
  IonList,
  IonListHeader,
  IonItem,
  IonLabel,
  IonCard,
  IonCardContent,
  IonCardHeader,
  IonCardTitle,
} from '@ionic/react';

function ProductList() {
  return (
    <>
      <IonList>
        <IonListHeader>
          <IonLabel>Featured Products</IonLabel>
        </IonListHeader>
        <IonItem>
          <IonLabel>Product 1</IonLabel>
        </IonItem>
        <IonItem>
          <IonLabel>Product 2</IonLabel>
        </IonItem>
      </IonList>

      <IonCard>
        <IonCardHeader>
          <IonCardTitle>Promotion</IonCardTitle>
        </IonCardHeader>
        <IonCardContent>
          Get 20% off on your first order!
        </IonCardContent>
      </IonCard>
    </>
  );
}
```

### Navigation

**Router Setup:**

```typescript
import { IonReactRouter } from '@ionic/react-router';
import { IonTabs, IonTabBar, IonTabButton, IonIcon, IonRouterOutlet } from '@ionic/react';
import { home, search, person } from 'ionicons/icons';

function MainApp() {
  return (
    <IonReactRouter>
      <IonTabs>
        <IonRouterOutlet>
          <Route path="/" render={() => <HomePage />} exact={true} />
          <Route path="/search" render={() => <SearchPage />} exact={true} />
          <Route path="/profile" render={() => <ProfilePage />} exact={true} />
        </IonRouterOutlet>

        <IonTabBar slot="bottom">
          <IonTabButton tab="home" href="/">
            <IonIcon icon={home} />
            <IonLabel>Home</IonLabel>
          </IonTabButton>
          <IonTabButton tab="search" href="/search">
            <IonIcon icon={search} />
            <IonLabel>Search</IonLabel>
          </IonTabButton>
          <IonTabButton tab="profile" href="/profile">
            <IonIcon icon={person} />
            <IonLabel>Profile</IonLabel>
          </IonTabButton>
        </IonTabBar>
      </IonTabs>
    </IonReactRouter>
  );
}
```

### Forms

```typescript
import { IonInput, IonButton, IonSelect, IonSelectOption, IonCheckbox } from '@ionic/react';
import { useState } from 'react';

function FormExample() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    role: 'user',
    newsletter: false,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Form submitted:', formData);
  };

  return (
    <form onSubmit={handleSubmit}>
      <IonInput
        label="Email"
        type="email"
        value={formData.email}
        onIonChange={(e) => setFormData({ ...formData, email: e.detail.value })}
        className="ion-margin"
      />

      <IonInput
        label="Password"
        type="password"
        value={formData.password}
        onIonChange={(e) => setFormData({ ...formData, password: e.detail.value })}
        className="ion-margin"
      />

      <IonSelect
        label="Role"
        value={formData.role}
        onIonChange={(e) => setFormData({ ...formData, role: e.detail.value })}
        className="ion-margin"
      >
        <IonSelectOption value="user">User</IonSelectOption>
        <IonSelectOption value="admin">Admin</IonSelectOption>
      </IonSelect>

      <IonCheckbox
        checked={formData.newsletter}
        onIonChange={(e) => setFormData({ ...formData, newsletter: e.detail.checked })}
        className="ion-margin"
      >
        Subscribe to newsletter
      </IonCheckbox>

      <IonButton expand="block" color="primary">
        Submit
      </IonButton>
    </form>
  );
}
```

### Theming

**CSS Variables:**

```css
/* Define theme variables */
:root {
  --ion-color-primary: #007aff;
  --ion-color-secondary: #32db64;
  --ion-color-tertiary: #ffc409;
  --ion-color-success: #10dc60;
  --ion-color-warning: #ffbb33;
  --ion-color-danger: #f53d3d;
  --ion-color-dark: #222428;
  --ion-color-medium: #989aa2;
  --ion-color-light: #f4f5f8;
}

/* Dark mode */
@media (prefers-color-scheme: dark) {
  :root {
    --ion-color-primary: #5b9aff;
    --ion-background-color: #121212;
    --ion-text-color: #ffffff;
  }
}
```

**Platform-Adaptive Styling:**

```typescript
import { getPlatforms } from '@ionic/react';

function PlatformAwareComponent() {
  const isIOS = getPlatforms().includes('ios');
  const isAndroid = getPlatforms().includes('android');

  return (
    <div className={isIOS ? 'ios-style' : isAndroid ? 'android-style' : 'web-style'}>
      Platform-specific content
    </div>
  );
}
```

### Gestures

```typescript
import { useGesture } from '@ionic/react';
import { useRef } from 'react';

function GestureExample() {
  const contentRef = useRef<HTMLDivElement>(null);
  const gesture = useGesture({
    el: contentRef.current,
    gestureName: 'swipe',
    gesureConfig: { direction: 'ltr' },
    onStart: () => console.log('Swipe started'),
    onMove: (detail) => console.log('Swiping', detail),
    onEnd: () => console.log('Swipe ended'),
  });

  return <div ref={contentRef}>Swipe me!</div>;
}
```

### Ionic Storage

```typescript
import { Storage } from '@ionic/storage';
import { useEffect, useState } from 'react';

const storage = new Storage();

function StorageExample() {
  const [data, setData] = useState<string | null>(null);

  useEffect(() => {
    storage.create();
  }, []);

  const saveData = async (key: string, value: string) => {
    await storage.set(key, value);
  };

  const getData = async (key: string) => {
    const value = await storage.get(key);
    setData(value);
  };

  const removeData = async (key: string) => {
    await storage.remove(key);
  };

  return (
    <div>
      <button onClick={() => saveData('myKey', 'myValue')}>Save</button>
      <button onClick={() => getData('myKey')}>Load</button>
      <button onClick={() => removeData('myKey')}>Delete</button>
      <p>Data: {data}</p>
    </div>
  );
}
```

---

## Progressive Web Apps (PWAs)

### Service Workers

**Registration and Lifecycle:**

```typescript
// Register service worker
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js', { scope: '/' })
    .then((registration) => {
      console.log('SW registered:', registration);

      // Check for updates periodically
      setInterval(() => {
        registration.update();
      }, 60000); // Check every minute
    })
    .catch((error) => {
      console.error('SW registration failed:', error);
    });

  // Listen for updates
  navigator.serviceWorker.addEventListener('controllerchange', () => {
    window.location.reload();
  });
}
```

### Caching Strategies

**Cache-First (Offline-First):**

```typescript
// service-worker.js
const CACHE_NAME = 'v1';
const urlsToCache = [
  '/',
  '/index.html',
  '/styles/main.css',
  '/js/app.js',
  '/images/logo.png',
];

// Install: populate cache
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(urlsToCache);
    })
  );
});

// Fetch: serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      if (response) {
        return response; // Serve from cache
      }

      return fetch(event.request).then((response) => {
        // Cache successful responses
        if (!response || response.status !== 200 || response.type !== 'basic') {
          return response;
        }

        const responseToCache = response.clone();
        caches.open(CACHE_NAME).then((cache) => {
          cache.put(event.request, responseToCache);
        });

        return response;
      });
    })
    .catch(() => {
      // Return offline page if available
      return caches.match('/offline.html');
    })
  );
});

// Activate: clean up old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((cacheName) => cacheName !== CACHE_NAME)
          .map((cacheName) => caches.delete(cacheName))
      );
    })
  );
});
```

**Network-First:**

```typescript
self.addEventListener('fetch', (event) => {
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // Cache successful responses
        const responseToCache = response.clone();
        caches.open(CACHE_NAME).then((cache) => {
          cache.put(event.request, responseToCache);
        });
        return response;
      })
      .catch(() => {
        // Fall back to cache
        return caches.match(event.request);
      })
  );
});
```

**Stale-While-Revalidate:**

```typescript
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      // Return cached version immediately
      const fetchPromise = fetch(event.request).then((response) => {
        const responseToCache = response.clone();
        caches.open(CACHE_NAME).then((cache) => {
          cache.put(event.request, responseToCache);
        });
        return response;
      });

      // Return cached version first, update in background
      return cachedResponse || fetchPromise;
    })
  );
});
```

### Web App Manifest

```json
{
  "name": "My Progressive Web App",
  "short_name": "MyPWA",
  "description": "A powerful PWA example",
  "start_url": "/",
  "scope": "/",
  "display": "standalone",
  "orientation": "portrait-primary",
  "background_color": "#ffffff",
  "theme_color": "#007aff",
  "icons": [
    {
      "src": "/images/icon-192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "/images/icon-512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "/images/icon-maskable-192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "maskable"
    }
  ],
  "screenshots": [
    {
      "src": "/images/screenshot1.png",
      "sizes": "540x720",
      "type": "image/png",
      "form_factor": "narrow"
    },
    {
      "src": "/images/screenshot2.png",
      "sizes": "1280x720",
      "type": "image/png",
      "form_factor": "wide"
    }
  ],
  "categories": ["productivity"],
  "shortcuts": [
    {
      "name": "New Task",
      "short_name": "Task",
      "description": "Create a new task",
      "url": "/new-task",
      "icons": [
        {
          "src": "/images/new-task-icon.png",
          "sizes": "192x192"
        }
      ]
    }
  ]
}
```

### Workbox

**Setup and Configuration:**

```bash
npm install workbox-cli --save-dev
npx workbox wizard --injectManifest
```

**workbox-config.js:**

```javascript
module.exports = {
  globDirectory: 'dist/',
  globPatterns: ['**/*.{js,css,html,png,jpg,svg}'],
  globIgnores: [
    '**/node_modules/**/*',
    '**/*.map',
  ],
  maximumFileSizeToCacheInBytes: 5 * 1024 * 1024, // 5MB
  swSrc: 'src/service-worker.js',
  swDest: 'dist/sw.js',
  dontCacheBustURLsMatching: /\.\w{8}\./,
  skipWaiting: true,
  clientsClaim: true,
};
```

**Advanced Service Worker with Workbox:**

```typescript
// src/service-worker.js
import { precacheAndRoute, cleanupOutdatedCaches } from 'workbox-precaching';
import { registerRoute } from 'workbox-routing';
import { CacheFirst, NetworkFirst, StaleWhileRevalidate } from 'workbox-strategies';
import { ExpirationPlugin } from 'workbox-expiration';

cleanupOutdatedCaches();

// Precache app shell
precacheAndRoute(self.__WB_MANIFEST);

// Cache images
registerRoute(
  ({ request }) => request.destination === 'image',
  new CacheFirst({
    cacheName: 'images',
    plugins: [
      new ExpirationPlugin({
        maxEntries: 50,
        maxAgeSeconds: 30 * 24 * 60 * 60, // 30 days
      }),
    ],
  })
);

// Network-first for API calls
registerRoute(
  ({ url }) => url.pathname.startsWith('/api/'),
  new NetworkFirst({
    cacheName: 'api-cache',
    plugins: [
      new ExpirationPlugin({
        maxAgeSeconds: 5 * 60, // 5 minutes
      }),
    ],
  })
);

// Stale-while-revalidate for HTML
registerRoute(
  ({ request }) => request.mode === 'navigate',
  new StaleWhileRevalidate({
    cacheName: 'html-cache',
  })
);
```

### Push Notifications (Web Push API)

**VAPID Key Generation:**

```bash
npm install web-push -g
web-push generate-vapid-keys
```

**Client Implementation:**

```typescript
async function subscribeToPushNotifications(vapidPublicKey: string) {
  if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
    console.error('Push notifications not supported');
    return;
  }

  const registration = await navigator.serviceWorker.ready;

  // Check if already subscribed
  let subscription = await registration.pushManager.getSubscription();

  if (!subscription) {
    subscription = await registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(vapidPublicKey),
    });
  }

  console.log('Push subscription:', subscription);

  // Send subscription to backend
  await fetch('/api/subscribe', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(subscription),
  });
}

function urlBase64ToUint8Array(base64String: string) {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);
  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}
```

**Service Worker Push Handler:**

```typescript
// service-worker.js
self.addEventListener('push', (event) => {
  const data = event.data?.json() ?? {};
  const options = {
    body: data.body || 'You have a new notification',
    icon: '/images/icon-192.png',
    badge: '/images/badge-72.png',
    tag: data.tag || 'default',
    requireInteraction: data.requireInteraction ?? false,
    actions: data.actions || [],
  };

  event.waitUntil(
    self.registration.showNotification(data.title || 'Notification', options)
  );
});

// Handle notification click
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  event.waitUntil(
    clients.matchAll({ type: 'window' }).then((clientList) => {
      if (clientList.length > 0) {
        return clientList[0].focus();
      }
      return clients.openWindow(event.notification.data?.url || '/');
    })
  );
});
```

### Background Sync

```typescript
// Register background sync
async function registerBackgroundSync() {
  const registration = await navigator.serviceWorker.ready;
  await registration.sync.register('sync-tasks');
}

// Service worker sync event
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-tasks') {
    event.waitUntil(
      fetch('/api/sync', { method: 'POST' })
        .then((response) => response.json())
        .catch(() => {
          // Retry sync on failure
          throw new Error('Sync failed');
        })
    );
  }
});
```

### Offline Storage

**IndexedDB:**

```typescript
const DB_NAME = 'myapp';
const STORE_NAME = 'items';

class ItemStore {
  private db: IDBDatabase | null = null;

  async init() {
    return new Promise<void>((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, 1);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve();
      };

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;
        db.createObjectStore(STORE_NAME, { keyPath: 'id' });
      };
    });
  }

  async addItem(item: any) {
    const tx = this.db!.transaction(STORE_NAME, 'readwrite');
    const store = tx.objectStore(STORE_NAME);
    return store.add(item);
  }

  async getItems() {
    const tx = this.db!.transaction(STORE_NAME, 'readonly');
    const store = tx.objectStore(STORE_NAME);
    return new Promise<any[]>((resolve, reject) => {
      const request = store.getAll();
      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(request.result);
    });
  }

  async deleteItem(id: string) {
    const tx = this.db!.transaction(STORE_NAME, 'readwrite');
    const store = tx.objectStore(STORE_NAME);
    return store.delete(id);
  }
}
```

### PWA Installability Criteria

**Requirements for App Install:**

1. Valid Web App Manifest with:
   - `name` or `short_name`
   - `start_url`
   - `display` (fullscreen, standalone, or minimal-ui)
   - 192×192 and 512×512 PNG icons

2. Service Worker with `fetch` event handler

3. HTTPS connection (except localhost)

4. Mobile-friendly viewport:
   ```html
   <meta name="viewport" content="width=device-width, initial-scale=1">
   ```

**Installation Prompt:**

```typescript
let deferredPrompt: BeforeInstallPromptEvent | null = null;

window.addEventListener('beforeinstallprompt', (event) => {
  event.preventDefault();
  deferredPrompt = event;

  // Show install button
  showInstallButton();
});

function showInstallButton() {
  const button = document.getElementById('install-btn');
  button?.addEventListener('click', async () => {
    if (deferredPrompt) {
      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      console.log(`User response: ${outcome}`);
      deferredPrompt = null;
    }
  });
}
```

---

## WebView Integration

### WKWebView (iOS)

**Swift Configuration:**

```swift
import WebKit

class ViewController: UIViewController, WKScriptMessageHandler {
  var webView: WKWebView!

  override func viewDidLoad() {
    super.viewDidLoad()

    let config = WKWebViewConfiguration()

    // Enable debugging
    if #available(iOS 16.4, *) {
      config.preferences.isElementInspectorEnabled = true
    }

    // Create web view
    webView = WKWebView(frame: view.bounds, configuration: config)
    view.addSubview(webView)

    // Add message handler
    config.userContentController.add(self, name: "nativeHandler")

    // JavaScript bridge
    let script = """
    window.native = {
      sendMessage: (data) => {
        webkit.messageHandlers.nativeHandler.postMessage(data)
      }
    }
    """

    let userScript = WKUserScript(
      source: script,
      injectionTime: .atDocumentStart,
      forMainFrameOnly: true
    )
    config.userContentController.addUserScript(userScript)

    // Load web content
    webView.load(URLRequest(url: URL(string: "file:///index.html")!))
  }

  // Handle messages from JavaScript
  func userContentController(
    _ userContentController: WKUserContentController,
    didReceive message: WKScriptMessage
  ) {
    guard let body = message.body as? [String: Any] else { return }

    if let action = body["action"] as? String {
      switch action {
      case "openCamera":
        openCamera()
      case "getLocation":
        getLocation()
      default:
        break
      }
    }
  }

  // Send message to JavaScript
  func sendToWebView(_ data: [String: Any]) {
    let encoder = JSONEncoder()
    let jsonData = try? encoder.encode(data)
    let jsonString = String(data: jsonData ?? Data(), encoding: .utf8) ?? "{}"

    webView.evaluateJavaScript("""
      window.nativeCallback('\(jsonString)')
    """)
  }
}
```

### Android WebView

**Kotlin Configuration:**

```kotlin
import android.webkit.WebView
import android.webkit.WebViewClient
import android.webkit.JavascriptInterface

class MainActivity : AppCompatActivity() {
  private lateinit var webView: WebView

  override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    setContentView(R.layout.activity_main)

    webView = findViewById(R.id.webview)

    // Configure WebView
    webView.settings.apply {
      javaScriptEnabled = true
      domStorageEnabled = true
      databaseEnabled = true
      mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW
    }

    // Add JavaScript interface
    webView.addJavascriptInterface(NativeBridge(this), "nativeBridge")

    // Set WebView client
    webView.webViewClient = object : WebViewClient() {
      override fun onPageFinished(view: WebView?, url: String?) {
        super.onPageFinished(view, url)
        // Inject JavaScript after page loads
        injectJavaScript()
      }
    }

    // Load web content
    webView.loadUrl("file:///android_asset/index.html")
  }

  private fun injectJavaScript() {
    val script = """
      window.native = {
        sendMessage: (data) => {
          nativeBridge.handleMessage(JSON.stringify(data))
        }
      }
    """
    webView.evaluateJavascript(script, null)
  }
}

class NativeBridge(private val context: Context) {
  @JavascriptInterface
  fun handleMessage(message: String) {
    val json = JSONObject(message)
    when (val action = json.getString("action")) {
      "openCamera" -> openCamera()
      "getLocation" -> getLocation()
    }
  }

  @JavascriptInterface
  fun sendToWebView(data: String) {
    // Send data back to web view via JavaScript callback
  }
}
```

### JavaScript Bridge Communication

**Pattern: Promise-based Async Communication**

```typescript
// Client-side JavaScript
class NativeBridge {
  private messageId = 0;
  private callbacks = new Map<number, { resolve: Function; reject: Function }>();

  constructor() {
    // Listen for responses from native
    window.addEventListener('nativeResponse', (event: any) => {
      const { id, data, error } = event.detail;
      const callback = this.callbacks.get(id);
      if (callback) {
        if (error) {
          callback.reject(new Error(error));
        } else {
          callback.resolve(data);
        }
        this.callbacks.delete(id);
      }
    });
  }

  async call(action: string, payload?: any): Promise<any> {
    return new Promise((resolve, reject) => {
      const id = this.messageId++;
      this.callbacks.set(id, { resolve, reject });

      const message = { id, action, payload };

      // Send to native
      if ((window as any).webkit) {
        // iOS
        (window as any).webkit.messageHandlers.nativeHandler.postMessage(message);
      } else if ((window as any).nativeBridge) {
        // Android
        (window as any).nativeBridge.handleMessage(JSON.stringify(message));
      }

      // Timeout
      setTimeout(() => {
        if (this.callbacks.has(id)) {
          reject(new Error('Native call timeout'));
          this.callbacks.delete(id);
        }
      }, 30000);
    });
  }

  async openCamera() {
    return this.call('openCamera');
  }

  async getLocation() {
    return this.call('getLocation');
  }
}

const native = new NativeBridge();
```

### Security: Content Security Policy

```html
<meta http-equiv="Content-Security-Policy" content="
  default-src 'self';
  script-src 'self' 'unsafe-inline' webkit-masked-url;
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https:;
  font-src 'self' data:;
  connect-src 'self' https: wss:;
  frame-ancestors 'none';
">
```

### Cookie Management

```swift
// iOS
let cookieStore = webView.configuration.websiteDataStore.httpCookieStore

// Set custom cookie
var cookies = HTTPCookie.cookies(
  withHeaders: ["Set-Cookie": "sessionId=abc123; Path=/; HttpOnly"],
  for: URL(string: "https://example.com")!
)
cookieStore.cookies(for: URL(string: "https://example.com")!) { existingCookies in
  let allCookies = (existingCookies ?? []) + cookies
  cookieStore.setCookies(allCookies)
}

// Clear cookies
let dataStore = WKWebsiteDataStore.default()
dataStore.fetchDataRecords(ofTypes: WKWebsiteDataTypeCookies) { records in
  dataStore.removeData(ofTypes: WKWebsiteDataTypeCookies, for: records) { }
}
```

---

## .NET MAUI

### Architecture and Handlers

**.NET MAUI** provides a single codebase for iOS, Android, macOS, and Windows using C# and XAML.

**Handler Pattern:**

```csharp
// XAML
<Button
  Text="Click Me"
  Clicked="OnButtonClicked"
  Padding="20"
  CornerRadius="10"
  FontSize="18" />

// C# Code-behind
private void OnButtonClicked(object sender, EventArgs e)
{
  DisplayAlert("Info", "Button clicked!", "OK");
}
```

### XAML vs C# Markup

**XAML (Traditional):**

```xml
<?xml version="1.0" encoding="utf-8" ?>
<ContentPage xmlns="http://schemas.microsoft.com/dotnet/2021/maui"
             xmlns:x="http://schemas.microsoft.com/winfx/2009/xaml"
             Title="Home Page">

  <ScrollView>
    <VerticalStackLayout Padding="30" Spacing="25">
      <Label Text="Welcome!" FontSize="32" FontAttributes="Bold" />

      <Entry Placeholder="Enter name" x:Name="NameEntry" />

      <Button
        Text="Submit"
        Clicked="OnSubmitClicked"
        BackgroundColor="#007AFF"
        TextColor="White" />
    </VerticalStackLayout>
  </ScrollView>

</ContentPage>
```

**C# Markup:**

```csharp
using Microsoft.Maui;
using Microsoft.Maui.Controls;
using Microsoft.Maui.Controls.Hosting;

namespace MyApp;

public class HomePage : ContentPage
{
  private Entry nameEntry = new();

  public HomePage()
  {
    Content = new ScrollView
    {
      Content = new VerticalStackLayout
      {
        Padding = 30,
        Spacing = 25,
        Children =
        {
          new Label
          {
            Text = "Welcome!",
            FontSize = 32,
            FontAttributes = FontAttributes.Bold
          },

          (nameEntry = new Entry { Placeholder = "Enter name" }),

          new Button
          {
            Text = "Submit",
            BackgroundColor = Colors.Blue,
            TextColor = Colors.White
          }.Invoke(b => b.Clicked += OnSubmitClicked)
        }
      }
    };
  }

  private void OnSubmitClicked(object sender, EventArgs e)
  {
    MainThread.BeginInvokeOnMainThread(async () =>
    {
      await DisplayAlert("Info", $"Hello {nameEntry.Text}", "OK");
    });
  }
}
```

### MVVM with CommunityToolkit

**ViewModel:**

```csharp
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using System.Collections.ObjectModel;

public partial class TasksViewModel : ObservableObject
{
  private readonly ITaskService _taskService;

  [ObservableProperty]
  private ObservableCollection<Task> tasks = new();

  [ObservableProperty]
  private string newTaskTitle = string.Empty;

  [ObservableProperty]
  private bool isLoading = false;

  [ObservableProperty]
  private string errorMessage = string.Empty;

  public TasksViewModel(ITaskService taskService)
  {
    _taskService = taskService;
  }

  [RelayCommand]
  public async Task LoadTasks()
  {
    try
    {
      IsLoading = true;
      ErrorMessage = string.Empty;

      var tasks = await _taskService.GetTasksAsync();
      Tasks = new ObservableCollection<Task>(tasks);
    }
    catch (Exception ex)
    {
      ErrorMessage = ex.Message;
    }
    finally
    {
      IsLoading = false;
    }
  }

  [RelayCommand]
  public async Task AddTask()
  {
    if (string.IsNullOrWhiteSpace(NewTaskTitle))
      return;

    try
    {
      var task = await _taskService.CreateTaskAsync(NewTaskTitle);
      Tasks.Add(task);
      NewTaskTitle = string.Empty;
    }
    catch (Exception ex)
    {
      ErrorMessage = ex.Message;
    }
  }

  [RelayCommand]
  public async Task DeleteTask(Task task)
  {
    try
    {
      await _taskService.DeleteTaskAsync(task.Id);
      Tasks.Remove(task);
    }
    catch (Exception ex)
    {
      ErrorMessage = ex.Message;
    }
  }
}
```

### Dependency Injection

**MauiProgram.cs:**

```csharp
using Microsoft.Maui.Hosting;

namespace MyApp;

public static class MauiProgram
{
  public static MauiApp CreateMauiApp()
  {
    var builder = MauiApp.CreateBuilder()
      .UseMauiApp<App>()
      .ConfigureFonts(fonts =>
      {
        fonts.AddFont("OpenSans-Regular.ttf", "OpenSansRegular");
      });

    // Register services
    builder.Services
      .AddSingleton<ITaskService, TaskService>()
      .AddSingleton<IHttpClientFactory>(_ => new HttpClientFactory())
      .AddSingleton<TasksViewModel>()
      .AddSingleton<TasksPage>();

    // Register SecureStorage
    builder.Services.AddSingleton(SecureStorage.Default);

    return builder.Build();
  }
}
```

### Navigation (Shell)

**AppShell.xaml:**

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<Shell
  x:Class="MyApp.AppShell"
  xmlns="http://schemas.microsoft.com/dotnet/2021/maui"
  xmlns:x="http://schemas.microsoft.com/winfx/2009/xaml"
  FlyoutBehavior="Disabled"
  BackgroundColor="#f0f0f0">

  <TabBar>
    <ShellContent
      Title="Tasks"
      Icon="list.png"
      ContentTemplate="{DataTemplate local:TasksPage}"
      Route="tasks" />

    <ShellContent
      Title="Settings"
      Icon="settings.png"
      ContentTemplate="{DataTemplate local:SettingsPage}"
      Route="settings" />
  </TabBar>

  <ShellContent
    Title="Task Details"
    ContentTemplate="{DataTemplate local:TaskDetailsPage}"
    Route="taskdetails/{taskId}" />

</Shell>
```

**Navigation in Code:**

```csharp
// Simple navigation
await Shell.Current.GoToAsync("settings");

// With parameters
await Shell.Current.GoToAsync($"taskdetails/{taskId}");

// Query parameters
await Shell.Current.GoToAsync($"search?query=urgent");

// Back navigation
await Shell.Current.GoToAsync("..");
```

### Platform-Specific Code

**Using #if Directives:**

```csharp
public partial class MainPage : ContentPage
{
  private void InitializePlatformFeatures()
  {
#if IOS
    // iOS-specific code
    StatusBar.SetColor(Colors.Blue);
#elif ANDROID
    // Android-specific code
    StatusBar.SetColor(Colors.Blue);
#elif WINDOWS
    // Windows-specific code
#endif
  }
}
```

**Platform-Specific Partials:**

```
ProjectStructure/
├── MainPage.xaml
├── MainPage.xaml.cs (shared)
├── Platforms/
│   ├── iOS/
│   │   └── MainPage.iOS.cs
│   ├── Android/
│   │   └── MainPage.Android.cs
│   └── Windows/
│       └── MainPage.Windows.cs
```

```csharp
// MainPage.xaml.cs
public partial class MainPage : ContentPage
{
  public void PlatformSpecificMethod()
  {
    PlatformSpecificImplementation();
  }

  private partial void PlatformSpecificImplementation();
}

// Platforms/iOS/MainPage.iOS.cs
public partial class MainPage
{
  private partial void PlatformSpecificImplementation()
  {
    // iOS implementation
  }
}
```

### HttpClient and Data Access

```csharp
public class TaskService : ITaskService
{
  private readonly IHttpClientFactory _httpClientFactory;
  private const string BaseUrl = "https://api.example.com";

  public TaskService(IHttpClientFactory httpClientFactory)
  {
    _httpClientFactory = httpClientFactory;
  }

  public async Task<List<Task>> GetTasksAsync()
  {
    using var client = _httpClientFactory.CreateClient();
    var response = await client.GetAsync($"{BaseUrl}/tasks");

    if (!response.IsSuccessStatusCode)
      throw new Exception($"API error: {response.StatusCode}");

    var json = await response.Content.ReadAsStringAsync();
    return JsonConvert.DeserializeObject<List<Task>>(json);
  }

  public async Task<Task> CreateTaskAsync(string title)
  {
    using var client = _httpClientFactory.CreateClient();

    var content = new StringContent(
      JsonConvert.SerializeObject(new { title }),
      Encoding.UTF8,
      "application/json"
    );

    var response = await client.PostAsync($"{BaseUrl}/tasks", content);
    var json = await response.Content.ReadAsStringAsync();
    return JsonConvert.DeserializeObject<Task>(json);
  }
}
```

### SQLite Database

**Database Context:**

```csharp
using SQLite;

public class AppDatabase
{
  private const string DatabaseFileName = "app.db3";
  private static string DatabasePath =>
    Path.Combine(FileSystem.AppDataDirectory, DatabaseFileName);

  private SQLiteAsyncConnection _connection;

  public SQLiteAsyncConnection Connection
  {
    get
    {
      if (_connection == null)
      {
        _connection = new SQLiteAsyncConnection(DatabasePath);
      }
      return _connection;
    }
  }

  public async Task InitializeAsync()
  {
    await Connection.CreateTableAsync<TaskModel>();
  }
}

[Table("tasks")]
public class TaskModel
{
  [PrimaryKey, AutoIncrement]
  public int Id { get; set; }

  [MaxLength(255)]
  public string Title { get; set; }

  public string Description { get; set; }

  public bool IsCompleted { get; set; }

  public DateTime CreatedAt { get; set; }
}

public class TaskRepository
{
  private readonly AppDatabase _database;

  public TaskRepository()
  {
    _database = new AppDatabase();
  }

  public async Task<List<TaskModel>> GetAllAsync()
  {
    return await _database.Connection.Table<TaskModel>().ToListAsync();
  }

  public async Task<int> InsertAsync(TaskModel task)
  {
    return await _database.Connection.InsertAsync(task);
  }

  public async Task<int> UpdateAsync(TaskModel task)
  {
    return await _database.Connection.UpdateAsync(task);
  }

  public async Task<int> DeleteAsync(int id)
  {
    return await _database.Connection.DeleteAsync<TaskModel>(id);
  }
}
```

### Publishing

**App.csproj Configuration:**

```xml
<Project Sdk="Microsoft.Maui.Sdk">
  <PropertyGroup>
    <UseMaui>true</UseMaui>
    <TargetFrameworks>net8.0-android;net8.0-ios;net8.0-maccatalyst;net8.0-windows10.0.19041.0</TargetFrameworks>

    <!-- iOS Signing -->
    <CodesignKey>iPhone Developer</CodesignKey>
    <CodesignEntitlements>Platforms/iOS/Entitlements.plist</CodesignEntitlements>

    <!-- Android Signing -->
    <AndroidKeyStore>true</AndroidKeyStore>
    <AndroidSigningKeyStore>MyKeyStore.keystore</AndroidSigningKeyStore>
    <AndroidSigningKeyAlias>myalias</AndroidSigningKeyAlias>
  </PropertyGroup>
</Project>
```

**Build Commands:**

```bash
# Android
dotnet publish -f net8.0-android -c Release

# iOS
dotnet publish -f net8.0-ios -c Release

# Windows
dotnet publish -f net8.0-windows10.0.19041.0 -c Release
```

---

## Tauri Mobile v2

### Architecture

Tauri Mobile uses Rust for the backend and web tech (HTML/CSS/JavaScript/React) for the frontend, communicating through IPC (Inter-Process Communication).

**Architecture Layers:**

```
┌──────────────────────┐
│  Web Frontend        │
│  (React/Vue)         │
├──────────────────────┤
│   Tauri JS Bridge    │
├──────────────────────┤
│   IPC Layer          │
├──────────────────────┤
│   Rust Backend       │
│   (Business Logic)   │
├──────────────────────┤
│   Native APIs        │
│   (via Plugins)      │
├──────────────────────┤
│   Device Hardware    │
└──────────────────────┘
```

### Project Setup

```bash
# Install Tauri CLI
npm install -D @tauri-apps/cli@next

# Create new project
npm create tauri-app@next -- --mobile

# Project structure
src/
├── main.rs (Rust backend)
├── lib.rs (Library code)
└── Commands.rs (IPC commands)

webroot/
├── src/
│   ├── App.tsx
│   └── main.tsx
└── package.json
```

### IPC Commands

**Rust Backend:**

```rust
// src-tauri/src/lib.rs
#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}!", name)
}

#[tauri::command]
async fn fetch_user_data(user_id: u32) -> Result<UserData, String> {
    // Async operation
    let data = get_user_from_db(user_id)
        .await
        .map_err(|e| e.to_string())?;
    Ok(data)
}

#[tauri::command]
fn process_image(image_path: String) -> Result<ProcessedImage, String> {
    let image = image::open(&image_path)
        .map_err(|e| e.to_string())?;

    // Process image
    let processed = apply_filters(image);

    Ok(processed)
}

pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            greet,
            fetch_user_data,
            process_image
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

**Frontend (React):**

```typescript
import { invoke } from '@tauri-apps/api/tauri';

async function callRustCommand() {
  try {
    const result = await invoke<string>('greet', { name: 'Alice' });
    console.log(result); // "Hello, Alice!"
  } catch (error) {
    console.error('Command error:', error);
  }
}

async function fetchData() {
  try {
    const userData = await invoke<UserData>('fetch_user_data', { userId: 123 });
    console.log(userData);
  } catch (error) {
    console.error('Fetch error:', error);
  }
}
```

### Plugin System

**Plugin Structure:**

```rust
// src-tauri/src/plugins/camera.rs
use tauri::{
    plugin::{Builder, TauriPlugin},
    Runtime,
};

pub fn init<R: Runtime>() -> TauriPlugin<R> {
    Builder::new("camera")
        .invoke_handler(tauri::generate_handler![
            open_camera,
            capture_photo
        ])
        .build()
}

#[tauri::command]
async fn open_camera() -> Result<String, String> {
    // Camera implementation
    Ok("Camera opened".to_string())
}

#[tauri::command]
async fn capture_photo() -> Result<Vec<u8>, String> {
    // Capture photo and return bytes
    Ok(vec![])
}
```

### Permissions System

**src-tauri/capabilities/main.json:**

```json
{
  "identifier": "main",
  "description": "Allows all core functionality",
  "windows": ["main"],
  "permissions": [
    "core:window:allow-internal-toggle-devtools",
    "core:window:allow-close",
    "core:app:allow-app-hide",
    "core:app:allow-app-show",
    "core:menu:allow-create",
    "core:menu:allow-append",
    "core:path:allow-resolve",
    "core:fs:allow-read-file",
    "core:fs:allow-write-file",
    "core:fs:allow-remove-file"
  ]
}
```

**Runtime Permissions Check:**

```rust
#[tauri::command]
fn access_camera(app: tauri::AppHandle) -> Result<(), String> {
    // Check permission at runtime
    let allowed = has_permission(&app, "camera:allow-access");
    if !allowed {
        return Err("Camera permission denied".to_string());
    }
    Ok(())
}
```

### Bundling for iOS/Android

**tauri.conf.json:**

```json
{
  "build": {
    "beforeBuildCommand": "npm run build",
    "devUrl": "http://localhost:5173",
    "frontendDist": "../dist"
  },
  "app": {
    "windows": [
      {
        "label": "main",
        "title": "MyApp",
        "url": "index.html"
      }
    ],
    "security": {
      "csp": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
    }
  },
  "bundle": {
    "active": true,
    "targets": ["ios", "android"],
    "ios": {
      "developmentTeam": "XXXXXXXXXX"
    },
    "android": {
      "useUrl": true
    }
  }
}
```

**Build Commands:**

```bash
# iOS
cargo tauri build --target ios

# Android
cargo tauri build --target android

# Development
cargo tauri dev
```

### Security Model

**Isolation Pattern:**

Tauri enforces a security model where:
- All IPC calls are type-safe
- Frontend code runs in a sandboxed WebView
- Backend has full system access (use carefully!)
- Permissions must be explicitly granted

```rust
// Secure file access
#[tauri::command]
fn read_app_file(filename: String, app: tauri::AppHandle) -> Result<String, String> {
    let app_dir = app.path_resolver().app_dir()
        .ok_or("Failed to get app directory")?;

    let file_path = app_dir.join(&filename);

    // Verify path is within app directory
    if !file_path.starts_with(&app_dir) {
        return Err("Invalid path".to_string());
    }

    std::fs::read_to_string(file_path)
        .map_err(|e| e.to_string())
}
```

### Comparison with Capacitor

| Feature | Capacitor | Tauri |
|---------|-----------|-------|
| Language | JavaScript/TypeScript | Rust + Web Tech |
| Performance | Good (native APIs) | Excellent (Rust) |
| Bundle Size | ~50MB | ~10-15MB |
| Memory | Moderate | Low |
| Learning Curve | Easy | Medium (Rust) |
| Native Access | Excellent | Direct (Rust) |
| Desktop Support | No | Yes (Windows/Mac/Linux) |
| Type Safety | Partial (TS) | Full (Rust) |
| Community Plugins | Large | Growing |

---

## Decision Matrix

### Framework Selection Guide

**Use Capacitor + Ionic when:**
- Team knows JavaScript/TypeScript
- Need rapid development
- Native API access is important
- Building for iOS/Android primarily
- Want extensive component library
- Team size: 2-10 developers

**Use .NET MAUI when:**
- Team uses C#/.NET
- Need multi-platform (iOS/Android/Windows/macOS)
- Enterprise requirements
- Want single codebase across all platforms
- Team size: 5-20 developers

**Use Tauri Mobile when:**
- Need high performance
- Team comfortable with Rust
- Want minimal bundle size
- Desktop + Mobile same codebase (with Tauri desktop)
- Need maximum security
- Team size: 3-15 developers

**Use PWA when:**
- App doesn't need offline-first
- Bandwidth-limited users
- No deep native feature needs
- Want easy distribution (no app stores)
- Building content-heavy app
- Team size: 1-5 developers

### Performance Comparison

| Metric | Capacitor | MAUI | Tauri | PWA |
|--------|-----------|------|-------|-----|
| Startup Time | 2-3s | 1-2s | 0.5s | <1s |
| Memory (idle) | 40-60MB | 50-80MB | 20-30MB | 15-25MB |
| Battery (8hr use) | 7-8h | 6-7h | 8h+ | 8h+ |
| Bundle Size | 30-60MB | 40-80MB | 10-20MB | 5-10MB |
| Native API Speed | Very Fast | Very Fast | Fast | N/A |

### API Access Comparison

```
Feature                Capacitor  MAUI  Tauri  PWA
────────────────────────────────────────────────
Camera                    ✓        ✓      ✓     Partial
Location                  ✓        ✓      ✓     ✓
Storage                   ✓        ✓      ✓     ✓
Push Notifications        ✓        ✓      ✓     ✓
Sensors                   ✓        ✓      ✓     Partial
File System               ✓        ✓      ✓     Limited
Contacts                  ✓        ✓      ✓     ✗
Payment Processing        ✓        ✓      ✓     ✓
Background Tasks          ✓        ✓      ✓     Limited
Bluetooth                 ✓        ✓      ✓     Partial
```

### Cost Analysis (6-month project)

| Factor | Capacitor | MAUI | Tauri | PWA |
|--------|-----------|------|-------|-----|
| Developer Velocity | High | High | Medium | Very High |
| Learning Curve | Low | Low | Medium | Very Low |
| Maintenance | Medium | Medium | High | Low |
| Distribution | App Stores | App Stores | App Stores | Web |
| Total Dev Cost | $$ | $$$ | $$ | $ |

---

## Production Checklist

**Pre-Release:**
- [ ] Security audit (OWASP compliance)
- [ ] Performance profiling (load testing)
- [ ] Accessibility testing (WCAG 2.1)
- [ ] Offline functionality verification
- [ ] Battery drain testing (24+ hours)
- [ ] Memory leak detection
- [ ] Push notification setup
- [ ] App signing certificates
- [ ] Privacy policy updated
- [ ] GDPR/privacy law compliance
- [ ] Analytics integration
- [ ] Crash reporting setup

**Release Process:**
- [ ] Version bump and CHANGELOG
- [ ] Build and sign binaries
- [ ] App Store/Play Store submission
- [ ] Beta testing (TestFlight/Google Play Beta)
- [ ] Staged rollout (25% → 50% → 100%)
- [ ] Monitor crash reports
- [ ] Monitor user feedback
- [ ] Prepare rollback plan

---

## Resources and References

- **Capacitor**: https://capacitorjs.com
- **Ionic**: https://ionicframework.com
- **PWA**: https://web.dev/progressive-web-apps
- **.NET MAUI**: https://learn.microsoft.com/maui
- **Tauri**: https://tauri.app
- **Web Push API**: https://developer.mozilla.org/en-US/docs/Web/API/Push_API
- **Service Workers**: https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API
- **WebView Security**: https://cheatsheetseries.owasp.org/cheatsheets/WebView_Transport_Security_Cheat_Sheet.html

---

*Last Updated: 2026-03-03*
*Reference Quality: Production-Grade*
*Scope: Comprehensive Hybrid & PWA Development*
