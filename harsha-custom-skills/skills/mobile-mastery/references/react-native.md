# React Native Comprehensive Reference Guide

## Table of Contents

- [1. Architecture](#1-architecture)
- [2. Project Setup](#2-project-setup)
- [3. Navigation](#3-navigation)
- [4. State Management](#4-state-management)
- [5. Styling](#5-styling)
- [6. Native Modules](#6-native-modules)
- [7. Performance Optimization](#7-performance-optimization)
- [8. Animations](#8-animations)
- [9. Testing](#9-testing)
- [10. Push Notifications](#10-push-notifications)
- [11. OTA Updates](#11-ota-updates)
- [12. Debugging](#12-debugging)
- [13. Common Pitfalls & Fixes](#13-common-pitfalls--fixes)

## 1. Architecture

### New Architecture vs Bridge

**New Architecture (Hermes + Fabric + TurboModules)**
- Synchronous method calls via JSI (JavaScript Interface)
- Native modules compile to native code (TurboModules)
- Improved performance and reduced memory footprint
- Direct C++ interoperability

Enable in `app.json`:
```json
{
  "expo": {
    "plugins": [
      [
        "react-native-worklets-core",
        {
          "architecture": "new"
        }
      ]
    ]
  }
}
```

**Legacy Bridge Architecture**
- Asynchronous batched calls via JSON serialization
- Older, slower but stable
- Used by most RN libraries not yet migrated

### Hermes Engine

```bash
# Enable Hermes for production builds (Android)
./gradlew assembleRelease -PenableHermes=true

# iOS (Podfile)
post_install do |installer|
  installer.pods_project.targets.each do |target|
    flutter_additional_ios_build_settings(target)
    target.build_configurations.each do |config|
      config.build_settings['GCC_PREPROCESSOR_DEFINITIONS'] ||= [
        '$(inherited)',
        'HERMES_ENABLE_DEBUGGER=1'
      ]
    end
  end
end
```

**Benefits**: 40% smaller bundle, 10% faster startup, 5% less memory

---

## 2. Project Setup

### Expo Managed vs Bare Workflow

**Expo Managed (Recommended for most)**
```bash
# Quick start
npx create-expo-app MyApp
cd MyApp
npm start

# With TypeScript
npx create-expo-app --template MyApp
```

**Bare CLI Workflow**
```bash
# Initialize with TypeScript
npx react-native init MyApp --template react-native-template-typescript

# Or with Expo in bare workflow
npx create-expo-app --template with-dev-client
```

### Project Structure
```
MyApp/
├── app/                    # Expo Router or navigation
│   ├── (tabs)/
│   ├── _layout.tsx
│   └── index.tsx
├── src/
│   ├── components/
│   │   ├── common/
│   │   └── screens/
│   ├── hooks/
│   ├── services/
│   │   ├── api.ts
│   │   └── storage.ts
│   ├── store/              # Redux/Zustand
│   ├── types/
│   │   └── index.ts
│   └── utils/
├── assets/
├── package.json
├── tsconfig.json
├── app.json
└── eas.json
```

### TypeScript Configuration
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["ES2020"],
    "jsx": "react-jsx",
    "moduleResolution": "node",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  }
}
```

---

## 3. Navigation

### React Navigation (Stack, Tab, Drawer)

**Stack Navigator**
```typescript
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

const Stack = createNativeStackNavigator();

export default function RootNavigator() {
  return (
    <NavigationContainer>
      <Stack.Navigator
        screenOptions={{
          headerShown: true,
          cardStyle: { backgroundColor: '#fff' },
          gestureEnabled: true,
        }}
      >
        <Stack.Screen
          name="Home"
          component={HomeScreen}
          options={{ title: 'Home' }}
        />
        <Stack.Screen
          name="Details"
          component={DetailsScreen}
          options={({ route }) => ({
            title: route.params?.name || 'Details',
          })}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
```

**Bottom Tab Navigator**
```typescript
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import Ionicons from '@expo/vector-icons/Ionicons';

const Tab = createBottomTabNavigator();

export default function TabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarIcon: ({ focused, color, size }) => {
          const icons = {
            Home: 'home',
            Explore: 'search',
            Profile: 'person',
          };
          return <Ionicons name={icons[route.name]} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#007AFF',
        tabBarInactiveTintColor: '#8E8E93',
      })}
    >
      <Tab.Screen name="Home" component={HomeScreen} />
      <Tab.Screen name="Explore" component={ExploreScreen} />
      <Tab.Screen name="Profile" component={ProfileScreen} />
    </Tab.Navigator>
  );
}
```

**Drawer Navigator**
```typescript
import { createDrawerNavigator } from '@react-navigation/drawer';

const Drawer = createDrawerNavigator();

export default function DrawerNavigator() {
  return (
    <Drawer.Navigator
      screenOptions={{
        headerShown: true,
        drawerPosition: 'left',
        swipeEnabled: true,
      }}
    >
      <Drawer.Screen name="Home" component={HomeScreen} />
      <Drawer.Screen name="Settings" component={SettingsScreen} />
    </Drawer.Navigator>
  );
}
```

### Expo Router (File-Based Routing)

```typescript
// app/_layout.tsx
import { Stack } from 'expo-router';

export default function RootLayout() {
  return (
    <Stack
      screenOptions={{
        headerShown: true,
        headerBackTitleVisible: false,
      }}
    >
      <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
      <Stack.Screen name="modal" options={{ presentation: 'modal' }} />
    </Stack>
  );
}

// app/(tabs)/_layout.tsx
import { Tabs } from 'expo-router';

export default function TabsLayout() {
  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: '#007AFF',
      }}
    >
      <Tabs.Screen name="index" options={{ title: 'Home' }} />
      <Tabs.Screen name="explore" options={{ title: 'Explore' }} />
    </Tabs>
  );
}
```

---

## 4. State Management

### Redux Toolkit

```typescript
import { createSlice, configureStore, PayloadAction } from '@reduxjs/toolkit';
import { TypedUseSelectorHook, useDispatch, useSelector } from 'react-redux';

// Slice
interface UserState {
  id: string | null;
  name: string;
  isLoading: boolean;
}

const initialState: UserState = {
  id: null,
  name: '',
  isLoading: false,
};

const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    setUser: (state, action: PayloadAction<{ id: string; name: string }>) => {
      state.id = action.payload.id;
      state.name = action.payload.name;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
  },
});

// Store
export const store = configureStore({
  reducer: {
    user: userSlice.reducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

// In component
export default function HomeScreen() {
  const dispatch = useAppDispatch();
  const user = useAppSelector((state) => state.user);

  return (
    <View>
      <Text>{user.name}</Text>
      <Button
        title="Load User"
        onPress={() => dispatch(userSlice.actions.setUser({ id: '1', name: 'John' }))}
      />
    </View>
  );
}
```

### Zustand (Lightweight Alternative)

```typescript
import { create } from 'zustand';

interface UserStore {
  user: { id: string; name: string } | null;
  setUser: (user: { id: string; name: string }) => void;
  clearUser: () => void;
}

export const useUserStore = create<UserStore>((set) => ({
  user: null,
  setUser: (user) => set({ user }),
  clearUser: () => set({ user: null }),
}));

// In component
export default function HomeScreen() {
  const { user, setUser } = useUserStore();

  return (
    <View>
      <Text>{user?.name}</Text>
      <Button title="Set User" onPress={() => setUser({ id: '1', name: 'John' })} />
    </View>
  );
}
```

### React Query/TanStack Query

```typescript
import { useQuery, useMutation, QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      gcTime: 1000 * 60 * 10,   // 10 minutes
      retry: 1,
    },
  },
});

// Fetch data
const fetchUsers = async () => {
  const response = await fetch('/api/users');
  return response.json();
};

// In component
export default function UsersScreen() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['users'],
    queryFn: fetchUsers,
  });

  if (isLoading) return <Text>Loading...</Text>;
  if (error) return <Text>Error loading users</Text>;

  return (
    <FlatList
      data={data}
      keyExtractor={(item) => item.id}
      renderItem={({ item }) => <Text>{item.name}</Text>}
    />
  );
}
```

---

## 5. Styling

### StyleSheet

```typescript
import { StyleSheet, View, Text } from 'react-native';

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: '#fff',
  },
  title: {
    fontSize: 24,
    fontWeight: '700',
    color: '#000',
    marginBottom: 16,
  },
  button: {
    paddingVertical: 12,
    paddingHorizontal: 16,
    backgroundColor: '#007AFF',
    borderRadius: 8,
    alignItems: 'center',
  },
  buttonText: {
    color: '#fff',
    fontWeight: '600',
  },
});

export default function StyledScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Welcome</Text>
      <Pressable style={styles.button}>
        <Text style={styles.buttonText}>Tap me</Text>
      </Pressable>
    </View>
  );
}
```

### NativeWind (Tailwind CSS)

```bash
npm install nativewind tailwindcss
npx tailwindcss init
```

```typescript
import { View, Text } from 'react-native';
import { styled } from 'nativewind';

const StyledView = styled(View);
const StyledText = styled(Text);

export default function StyledScreen() {
  return (
    <StyledView className="flex-1 bg-white p-4">
      <StyledText className="text-2xl font-bold text-gray-900 mb-4">
        Welcome
      </StyledText>
      <StyledView className="bg-blue-500 rounded-lg p-3">
        <StyledText className="text-white font-semibold text-center">
          Tap me
        </StyledText>
      </StyledView>
    </StyledView>
  );
}
```

### Tamagui

```bash
npm install tamagui @tamagui/config
```

```typescript
import { TamaguiProvider, Button, Text, YStack } from 'tamagui';
import { config } from '@tamagui/config/v3';

export default function StyledScreen() {
  return (
    <TamaguiProvider config={config}>
      <YStack flex={1} bg="white" p="$4" space="$4">
        <Text size="$6" weight="bold">
          Welcome
        </Text>
        <Button bg="$blue10">Tap me</Button>
      </YStack>
    </TamaguiProvider>
  );
}
```

---

## 6. Native Modules

### Auto-linking

```bash
# Install a library with native code
npm install react-native-camera

# Auto-link (React Native 0.60+)
npx react-native link react-native-camera

# For Expo
npx expo prebuild
```

### TurboModule (New Architecture)

```typescript
// TurboModule declaration (native.ts)
import type {
  TurboModule,
} from 'react-native';
import { TurboModuleRegistry } from 'react-native';

export interface Spec extends TurboModule {
  getConstants(): {
    VERSION: string;
  };
  getString(options: string): Promise<string>;
}

export default TurboModuleRegistry.getEnforcing<Spec>(
  'MyNativeModule'
);

// Usage
import MyNativeModule from './native';

export default function App() {
  const [text, setText] = useState('');

  useEffect(() => {
    MyNativeModule.getString('hello').then(setText);
  }, []);

  return <Text>{text}</Text>;
}
```

### Native Bridge (Legacy)

```typescript
import { NativeModules } from 'react-native';

const { MyNativeModule } = NativeModules;

export default function App() {
  const handlePress = async () => {
    try {
      const result = await MyNativeModule.calculateSum(5, 3);
      console.log('Result:', result);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <Button title="Call Native" onPress={handlePress} />
  );
}
```

---

## 7. Performance Optimization

### Hermes Configuration

```json
{
  "expo": {
    "plugins": [
      [
        "expo-build-properties",
        {
          "android": {
            "enableHermes": true
          },
          "ios": {
            "useFrameworks": "static"
          }
        }
      ]
    ]
  }
}
```

### FlatList Optimization

```typescript
<FlatList
  data={largeList}
  renderItem={({ item }) => <UserItem user={item} />}
  keyExtractor={(item) => item.id}
  removeClippedSubviews={true}
  maxToRenderPerBatch={10}
  updateCellsBatchingPeriod={50}
  initialNumToRender={20}
  windowSize={10}
  onEndReachedThreshold={0.5}
  onEndReached={() => loadMore()}
  getItemLayout={(data, index) => ({
    length: ITEM_HEIGHT,
    offset: ITEM_HEIGHT * index,
    index,
  })}
/>
```

### memo, useMemo, useCallback

```typescript
import { memo, useMemo, useCallback } from 'react';

// Memoized component
const UserItem = memo(({ user, onPress }) => {
  return (
    <Pressable onPress={onPress}>
      <Text>{user.name}</Text>
    </Pressable>
  );
});

// In parent component
export default function UsersScreen() {
  const [users, setUsers] = useState([]);

  const sortedUsers = useMemo(() => {
    return users.sort((a, b) => a.name.localeCompare(b.name));
  }, [users]);

  const handleUserPress = useCallback((userId) => {
    navigation.navigate('Details', { userId });
  }, [navigation]);

  return (
    <FlatList
      data={sortedUsers}
      renderItem={({ item }) => (
        <UserItem user={item} onPress={() => handleUserPress(item.id)} />
      )}
      keyExtractor={(item) => item.id}
    />
  );
}
```

### Bundle Analysis

```bash
# Generate bundle
npx react-native bundle --entry-file index.js --platform android --dev false --bundle-output android.bundle

# Analyze
npx ts-bundle-analyzer android.bundle
```

---

## 8. Animations

### Reanimated 3

```bash
npm install react-native-reanimated
npx expo prebuild
```

```typescript
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
} from 'react-native-reanimated';

export default function AnimatedButton() {
  const scale = useSharedValue(1);

  const animatedStyle = useAnimatedStyle(() => {
    return {
      transform: [{ scale: scale.value }],
    };
  });

  return (
    <Animated.View style={[styles.box, animatedStyle]}>
      <Pressable
        onPressIn={() => {
          scale.value = withSpring(0.95);
        }}
        onPressOut={() => {
          scale.value = withSpring(1);
        }}
      >
        <Text>Tap me</Text>
      </Pressable>
    </Animated.View>
  );
}
```

### Gesture Handler

```bash
npm install react-native-gesture-handler
```

```typescript
import { GestureDetector, Gesture } from 'react-native-gesture-handler';
import Animated from 'react-native-reanimated';

export default function SwipeableScreen() {
  const translateX = useSharedValue(0);

  const pan = Gesture.Pan()
    .onUpdate((event) => {
      translateX.value = event.translationX;
    })
    .onEnd(() => {
      translateX.value = withSpring(0);
    });

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ translateX: translateX.value }],
  }));

  return (
    <GestureDetector gesture={pan}>
      <Animated.View style={[styles.box, animatedStyle]} />
    </GestureDetector>
  );
}
```

### Lottie

```bash
npm install lottie-react-native
```

```typescript
import LottieView from 'lottie-react-native';

export default function AnimationScreen() {
  return (
    <LottieView
      source={require('./animations/loading.json')}
      autoPlay
      loop
      style={{ width: 200, height: 200 }}
    />
  );
}
```

---

## 9. Testing

### Jest Unit Tests

```typescript
// math.test.ts
describe('math functions', () => {
  it('should add two numbers', () => {
    expect(add(2, 3)).toBe(5);
  });

  it('should handle negative numbers', () => {
    expect(add(-2, 3)).toBe(1);
  });
});
```

### React Native Testing Library

```typescript
import { render, screen, fireEvent } from '@testing-library/react-native';
import HomeScreen from './HomeScreen';

describe('HomeScreen', () => {
  it('renders welcome message', () => {
    render(<HomeScreen />);
    expect(screen.getByText('Welcome')).toBeTruthy();
  });

  it('calls onPress when button tapped', () => {
    const onPress = jest.fn();
    render(<HomeScreen onPress={onPress} />);
    fireEvent.press(screen.getByRole('button'));
    expect(onPress).toHaveBeenCalled();
  });
});
```

### Detox E2E Testing

```bash
npm install detox-cli detox detox-config
```

```typescript
// e2e/firstTest.e2e.js
describe('Login Flow', () => {
  beforeAll(async () => {
    await device.launchApp();
  });

  beforeEach(async () => {
    await device.reloadReactNative();
  });

  it('should login successfully', async () => {
    await element(by.id('email-input')).typeText('test@example.com');
    await element(by.id('password-input')).typeText('password123');
    await element(by.id('login-button')).multiTap(1);
    await expect(element(by.text('Home Screen'))).toBeVisible();
  });
});
```

---

## 10. Push Notifications

### Expo Notifications

```bash
npm install expo-notifications
```

```typescript
import * as Notifications from 'expo-notifications';
import { useEffect } from 'react';

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: false,
    shouldSetBadge: false,
  }),
});

export default function NotificationScreen() {
  useEffect(() => {
    const subscription = Notifications.addNotificationResponseReceivedListener(
      (response) => {
        console.log('Notification tapped:', response);
      }
    );

    return () => subscription.remove();
  }, []);

  const sendNotification = async () => {
    await Notifications.scheduleNotificationAsync({
      content: {
        title: 'Hello!',
        body: 'This is a test notification',
        data: { action: 'open_home' },
      },
      trigger: { seconds: 2 },
    });
  };

  return (
    <Button title="Send Notification" onPress={sendNotification} />
  );
}
```

### Firebase Cloud Messaging (FCM)

```typescript
import messaging from '@react-native-firebase/messaging';

export async function requestNotificationPermission() {
  const authStatus = await messaging().requestPermission();
  return authStatus === messaging.AuthorizationStatus.AUTHORIZED;
}

export function setupNotificationListeners() {
  // Handle notification when app is in foreground
  const unsubscribe = messaging().onMessage(async (remoteMessage) => {
    console.log('Notification received:', remoteMessage);
  });

  // Handle notification when app is launched from notification
  messaging().onNotificationOpenedApp((remoteMessage) => {
    if (remoteMessage?.notification) {
      navigation.navigate(remoteMessage.data?.screen);
    }
  });

  return unsubscribe;
}
```

---

## 11. OTA Updates

### EAS Update

```bash
npm install expo-updates
npx eas update:configure
npx eas update
```

```json
{
  "expo": {
    "updates": {
      "url": "https://u.expo.dev/YOUR_PROJECT_ID",
      "enabled": true,
      "checkAutomatically": "ON_APP_START",
      "fallbackToCacheTimeout": 0
    },
    "runtimeVersion": "1.0.0"
  }
}
```

```typescript
import * as Updates from 'expo-updates';
import { useEffect } from 'react';

export default function App() {
  useEffect(() => {
    const checkForUpdates = async () => {
      try {
        const update = await Updates.checkForUpdateAsync();
        if (update.isAvailable) {
          await Updates.fetchUpdateAsync();
          await Updates.reloadAsync();
        }
      } catch (error) {
        console.error('Error checking for updates:', error);
      }
    };

    checkForUpdates();
  }, []);

  return <HomeScreen />;
}
```

### CodePush (Microsoft AppCenter)

```bash
npm install react-native-code-push
npx react-native link react-native-code-push
```

```typescript
import codePush from 'react-native-code-push';

let App = () => {
  return <HomeScreen />;
};

App = codePush({
  checkFrequency: codePush.CheckFrequency.ON_APP_START,
  installMode: codePush.InstallMode.ON_NEXT_RESTART,
})(App);

export default App;
```

---

## 12. Debugging

### Flipper

```bash
# Install Flipper from https://fbflipper.com
# Then add to React Native project
npx react-native-community/cli install flipper-ios
```

**Access Flipper Console**:
1. Open Flipper Desktop
2. Select your device
3. View logs, inspect Redux state, mock network responses

### React DevTools

```bash
npm install --save-dev @react-devtools/core
```

```typescript
import { getDevTools } from '@react-devtools/core';

if (__DEV__) {
  getDevTools().init();
}
```

### LogBox Configuration

```typescript
import { LogBox } from 'react-native';

// Disable specific warnings
LogBox.ignoreLogs(['Non-serializable values']);
LogBox.ignoreAllLogs(false); // Enable in production

// Custom error handler
const originalError = console.error;
console.error = (...args) => {
  if (args[0]?.includes?.('YellowBox')) return;
  originalError.call(console, ...args);
};
```

---

## 13. Common Pitfalls & Fixes

### 1. **Memory Leaks in useEffect**
```typescript
// WRONG
useEffect(() => {
  const subscription = listener.subscribe(() => {});
}, []);

// CORRECT
useEffect(() => {
  const subscription = listener.subscribe(() => {});
  return () => subscription.unsubscribe();
}, []);
```

### 2. **Missing Key Props in Lists**
```typescript
// WRONG
{items.map((item, index) => <Item key={index} data={item} />)}

// CORRECT
{items.map((item) => <Item key={item.id} data={item} />)}
```

### 3. **Image Size Not Set**
```typescript
// WRONG
<Image source={require('./photo.png')} />

// CORRECT
<Image
  source={require('./photo.png')}
  style={{ width: 200, height: 200 }}
/>
```

### 4. **FlatList Not Rendering**
```typescript
// WRONG
<FlatList data={data} renderItem={renderItem} />

// CORRECT
<FlatList
  data={data}
  renderItem={renderItem}
  keyExtractor={(item) => item.id.toString()}
/>
```

### 5. **Navigation State Issues**
```typescript
// WRONG
navigation.navigate('Screen', { id: null });

// CORRECT
if (id !== null) {
  navigation.navigate('Screen', { id });
}
```

### 6. **Performance Regression from Re-renders**
```typescript
// WRONG
const Component = () => {
  const handlePress = () => console.log('pressed');
  return <Button onPress={handlePress} />;
};

// CORRECT
const Component = () => {
  const handlePress = useCallback(() => console.log('pressed'), []);
  return <Button onPress={handlePress} />;
};
```

### 7. **Async State Updates After Unmount**
```typescript
// WRONG
useEffect(() => {
  fetch('/api/data').then((data) => setState(data));
}, []);

// CORRECT
useEffect(() => {
  let isMounted = true;
  fetch('/api/data').then((data) => {
    if (isMounted) setState(data);
  });
  return () => {
    isMounted = false;
  };
}, []);
```

### 8. **Untrusted Dependency Arrays**
```typescript
// WRONG
useEffect(() => {
  // complex logic
}, [navigation]); // navigation object changes every render

// CORRECT
useEffect(() => {
  // complex logic
}, [navigation?.isFocused]);
```

### 9. **Platform-Specific Code Issues**
```typescript
// WRONG
const styles = StyleSheet.create({
  container: {
    marginTop: 20, // Different on iOS vs Android
  },
});

// CORRECT
import { Platform } from 'react-native';

const styles = StyleSheet.create({
  container: {
    marginTop: Platform.OS === 'ios' ? 20 : 10,
  },
});
```

### 10. **Heavy Computations on Main Thread**
```typescript
// WRONG
const expensiveList = data.sort().filter().map(); // Blocks UI

// CORRECT
import { useWorkerThread } from 'react-native-worker-threads';

const [processedData] = useWorkerThread(
  () => data.sort().filter().map(),
  [data]
);
```

---

## Quick Reference

**Install essentials**:
```bash
npm install @react-navigation/native @react-navigation/bottom-tabs
npm install @reduxjs/toolkit react-redux
npm install axios
npm install react-native-gesture-handler react-native-reanimated
```

**TypeScript setup**:
```bash
npx create-expo-app --template
```

**Test setup**:
```bash
npm install --save-dev @testing-library/react-native jest
```

**EAS build**:
```bash
npm install --global eas-cli
eas build --platform android
```
