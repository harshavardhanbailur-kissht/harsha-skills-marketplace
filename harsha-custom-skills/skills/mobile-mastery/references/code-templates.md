# Mobile App Development: Reusable Code Templates

Reference guide with production-quality templates for rapid mobile app scaffolding. Each template includes clear customization points and framework-specific implementations.

## Table of Contents

- [Project Scaffolding Templates](#1-project-scaffolding-templates)
- [Feature Module Template](#2-feature-module-template)
- [API Layer Template](#3-api-layer-template)
- [Authentication Flow Template](#4-authentication-flow-template)
- [Repository Pattern Template](#5-repository-pattern-template)
- [List/Feed Screen Template](#6-listfeed-screen-template)
- [Form Screen Template](#7-form-screen-template)
- [Settings Screen Template](#8-settings-screen-template)
- [Error Handling Pattern](#9-error-handling-pattern)
- [Navigation Setup Template](#10-navigation-setup-template)
- [Quick Reference: Framework Selection Guide](#quick-reference-framework-selection-guide)
- [Best Practices Across All Templates](#best-practices-across-all-templates)

---

## 1. Project Scaffolding Templates

### React Native/Expo (Feature-First Structure)

```
my-app/
├── app.json                          # Expo config
├── App.tsx                           # Root component
├── src/
│   ├── navigation/
│   │   ├── RootNavigator.tsx         # Tab + Stack nav setup
│   │   └── types.ts                  # Navigation type defs
│   ├── features/
│   │   ├── auth/
│   │   │   ├── screens/
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   ├── services/
│   │   │   └── store.ts              # Redux/Zustand slice
│   │   ├── home/
│   │   ├── profile/
│   │   └── settings/
│   ├── shared/
│   │   ├── api/
│   │   │   ├── client.ts             # Axios instance
│   │   │   └── interceptors.ts
│   │   ├── components/               # Reusable UI components
│   │   ├── hooks/                    # Custom hooks (useAsync, etc)
│   │   ├── utils/
│   │   └── types/
│   └── theme/
│       └── colors.ts, typography.ts
├── __tests__/                        # Mirror feature structure
└── package.json
```

When to use: Scalable apps with 3+ features, team development, modular feature releases.

---

### Flutter (Feature-First Structure)

```
lib/
├── main.dart                         # Entry, theme, nav setup
├── config/
│   ├── routes/
│   │   └── app_router.dart           # GoRouter or GetX config
│   └── constants/
├── features/
│   ├── auth/
│   │   ├── presentation/
│   │   │   ├── pages/
│   │   │   ├── widgets/
│   │   │   └── providers/            # Riverpod/Provider
│   │   ├── domain/
│   │   │   ├── entities/
│   │   │   └── repositories/
│   │   └── data/
│   │       ├── datasources/
│   │       ├── models/
│   │       └── repositories/
│   ├── home/
│   ├── profile/
│   └── settings/
├── shared/
│   ├── widgets/
│   ├── theme/
│   ├── utils/
│   └── services/
└── pubspec.yaml
```

When to use: Cross-platform iOS/Android with native performance, apps requiring hot reload development.

---

### SwiftUI (iOS Feature-First)

```
MyApp/
├── MyApp.swift                       # @main App entry
├── Navigation/
│   ├── AppCoordinator.swift          # Navigation state
│   └── NavigationPath+Routes.swift
├── Features/
│   ├── Auth/
│   │   ├── Screens/
│   │   │   ├── LoginView.swift
│   │   │   └── SignupView.swift
│   │   ├── ViewModels/
│   │   ├── Models/
│   │   └── Services/
│   ├── Home/
│   ├── Profile/
│   └── Settings/
├── Shared/
│   ├── Components/
│   ├── Network/
│   ├── Utils/
│   └── Extensions/
├── Resources/
│   └── Assets.xcassets
└── MyApp.swift
```

When to use: iOS-only or Mac Catalyst apps, native performance critical, AppKit integration needed.

---

### Jetpack Compose (Android Feature-First)

```
app/src/main/java/com/example/app/
├── MainActivity.kt                   # Entry point
├── navigation/
│   ├── NavGraph.kt                   # Composable nav setup
│   └── Routes.kt                     # Route definitions
├── features/
│   ├── auth/
│   │   ├── presentation/
│   │   │   ├── screens/
│   │   │   ├── composables/
│   │   │   └── AuthViewModel.kt
│   │   ├── domain/
│   │   │   ├── entities/
│   │   │   └── usecases/
│   │   └── data/
│   │       ├── api/
│   │       ├── local/
│   │       └── repository/
│   ├── home/
│   ├── profile/
│   └── settings/
├── shared/
│   ├── ui/
│   │   ├── components/
│   │   ├── theme/
│   │   └── extensions/
│   ├── network/
│   └── utils/
└── di/
    └── AppModule.kt                  # Hilt DI setup
```

When to use: Android-first apps, leveraging Material 3 design, Compose performance benefits.

---

## 2. Feature Module Template

### Standard Feature Structure (Framework-Agnostic Pattern)

```
feature_name/
├── README.md                         # Feature documentation
├── screens/                          # UI pages
│   ├── ListScreen.tsx                # or .swift, .kt
│   └── DetailScreen.tsx
├── components/                       # Reusable within feature
│   ├── FeatureCard.tsx
│   └── FeatureHeader.tsx
├── hooks/                            # (React) Custom logic
│   └── useFeatureData.ts
├── services/                         # API calls, business logic
│   └── featureApi.ts
├── store/                            # (React) State management
│   └── featureSlice.ts               # Redux or Zustand
├── types/                            # Feature-specific types
│   └── feature.types.ts
├── navigation.ts                     # Feature routing setup
├── __tests__/                        # Unit + integration tests
│   ├── screens.test.tsx
│   ├── services.test.ts
│   └── hooks.test.ts
└── index.ts                          # Public exports only
```

When to use: Adding new functionality with clear boundaries, enabling feature team ownership.

Customization points:
- Replace `hooks` with Riverpod providers (Flutter), ViewModels (Android), @ObservedObject (SwiftUI)
- Replace `store` with Redux, Zustand, MobX, Jotai, or state management of choice
- Add `viewmodels` folder if using MVVM pattern
- Add `domain` folder if using Clean Architecture (entities, use cases)

---

## 3. API Layer Template

### HTTP Client Setup (Universal Pattern)

```typescript
// src/shared/api/client.ts
// TODO: Customize base URL, timeout, and auth header name

interface ApiConfig {
  baseURL: string;
  timeout: number;
  authHeaderName: string; // 'Authorization' or custom
}

interface ApiResponse<T> {
  success: boolean;
  data: T;
  error?: {
    code: string;
    message: string;
    retryable: boolean;
  };
}

// Framework-specific implementations below:
```

### React Native (Axios + Interceptors)

```typescript
// src/shared/api/client.ts
import axios, { AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import { AuthService } from '@/features/auth/services/authService';

const createApiClient = (): AxiosInstance => {
  const client = axios.create({
    baseURL: process.env.REACT_APP_API_URL || 'https://api.example.com',
    timeout: 30000,
  });

  // Request interceptor: Add auth token
  client.interceptors.request.use(async (config: InternalAxiosRequestConfig) => {
    const token = await AuthService.getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  });

  // Response interceptor: Handle 401, retry with refresh
  client.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config;
      if (error.response?.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;
        try {
          const newToken = await AuthService.refreshToken();
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          return client(originalRequest);
        } catch {
          await AuthService.logout();
          return Promise.reject(error);
        }
      }
      return Promise.reject(error);
    }
  );

  return client;
};

export const apiClient = createApiClient();
```

When to use: React Native/Expo apps, any JavaScript-based mobile platform.

---

### Android (Ktor HTTP Client)

```kotlin
// app/src/main/java/com/example/app/shared/network/HttpClientFactory.kt
import io.ktor.client.*
import io.ktor.client.engine.okhttp.*
import io.ktor.client.plugins.*
import io.ktor.client.plugins.auth.*
import io.ktor.client.plugins.auth.providers.*
import io.ktor.client.plugins.logging.*

object HttpClientFactory {
    // TODO: Customize timeout and base URL
    private const val REQUEST_TIMEOUT = 30000L

    fun create(authService: AuthService): HttpClient = HttpClient(OkHttp) {
        install(DefaultRequest) {
            url("https://api.example.com") // TODO: Customize
        }

        install(HttpTimeout) {
            requestTimeoutMillis = REQUEST_TIMEOUT
            connectTimeoutMillis = REQUEST_TIMEOUT
        }

        install(Auth) {
            bearer {
                loadTokens { authService.getToken() }
                refreshTokens {
                    authService.refreshToken()
                }
            }
        }

        install(HttpRequestRetry) {
            retryOnServerErrors(maxRetries = 3)
            exponentialDelay(initialDelay = 100, maxDelay = 5000)
        }

        install(Logging) {
            logger = Logger.DEFAULT
            level = LogLevel.ALL
        }
    }
}
```

When to use: Android Compose/Views apps, Kotlin ecosystem preferred.

---

### iOS (URLSession + Combine)

```swift
// Shared/Network/APIClient.swift
import Foundation
import Combine

// TODO: Customize endpoints and error types
class APIClient {
    private let session: URLSession
    private let baseURL: URL
    @Published var authToken: String?

    init(baseURL: URL = URL(string: "https://api.example.com")!) {
        self.baseURL = baseURL
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30
        config.waitsForConnectivity = true
        self.session = URLSession(configuration: config)
    }

    func request<T: Decodable>(
        endpoint: String,
        method: HTTPMethod = .get,
        body: Encodable? = nil
    ) -> AnyPublisher<T, APIError> {
        var request = URLRequest(url: baseURL.appendingPathComponent(endpoint))
        request.httpMethod = method.rawValue

        if let token = authToken {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        if let body = body {
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
            request.httpBody = try? JSONEncoder().encode(body)
        }

        return session.dataTaskPublisher(for: request)
            .mapError { _ in APIError.networkError }
            .flatMap { data, response -> AnyPublisher<T, APIError> in
                guard let http = response as? HTTPURLResponse else {
                    return Fail(error: .networkError).eraseToAnyPublisher()
                }

                if http.statusCode == 401 {
                    return self.refreshTokenAndRetry(request: request)
                }

                return Just((data, http.statusCode))
                    .tryMap { data, code in
                        guard 200..<300 ~= code else {
                            throw APIError.serverError(code)
                        }
                        return try JSONDecoder().decode(T.self, from: data)
                    }
                    .mapError { error in
                        (error as? APIError) ?? .decodingError
                    }
                    .eraseToAnyPublisher()
            }
            .eraseToAnyPublisher()
    }

    private func refreshTokenAndRetry<T: Decodable>(
        request: URLRequest
    ) -> AnyPublisher<T, APIError> {
        // TODO: Implement token refresh logic
        return Fail(error: .unauthorized).eraseToAnyPublisher()
    }
}

enum HTTPMethod: String {
    case get = "GET"
    case post = "POST"
    case put = "PUT"
    case delete = "DELETE"
}

enum APIError: LocalizedError {
    case networkError
    case serverError(Int)
    case decodingError
    case unauthorized
    case unknown
}
```

When to use: iOS/macOS apps, Combine-based reactive programming.

---

## 4. Authentication Flow Template

### Complete Auth Flow (React Native)

```typescript
// src/features/auth/screens/AuthStack.tsx
// TODO: Customize OAuth provider IDs and endpoints

const AuthStack = () => {
  const [authState, dispatch] = useReducer(authReducer, initialState);

  const handleLogin = async (email: string, password: string) => {
    try {
      dispatch({ type: 'LOGIN_START' });
      const response = await authApi.login({ email, password });
      await SecureStore.setItem('authToken', response.token);
      dispatch({ type: 'LOGIN_SUCCESS', payload: response.user });
    } catch (error) {
      dispatch({ type: 'LOGIN_ERROR', payload: error.message });
    }
  };

  const handleBiometric = async () => {
    // TODO: Implement Face/Touch ID authentication
    try {
      const authenticated = await BiometricAuth.authenticate();
      if (authenticated) {
        const token = await SecureStore.getItem('authToken');
        // Validate and refresh token
        dispatch({ type: 'BIOMETRIC_SUCCESS' });
      }
    } catch (error) {
      dispatch({ type: 'BIOMETRIC_ERROR' });
    }
  };

  const handleOAuth = async (provider: 'google' | 'apple') => {
    // TODO: Configure OAuth client IDs
    try {
      const credential = await OAuthService.authenticate(provider);
      const response = await authApi.oauthLogin(credential);
      await SecureStore.setItem('authToken', response.token);
      dispatch({ type: 'LOGIN_SUCCESS', payload: response.user });
    } catch (error) {
      dispatch({ type: 'LOGIN_ERROR', payload: error.message });
    }
  };

  const handleLogout = async () => {
    try {
      await authApi.logout();
      await SecureStore.removeItem('authToken');
      dispatch({ type: 'LOGOUT' });
    } catch (error) {
      console.error('Logout error:', error);
      // Force logout anyway
      dispatch({ type: 'LOGOUT' });
    }
  };

  if (authState.status === 'idle') {
    return <SplashScreen />;
  }

  if (authState.isSignedIn) {
    return <AppStack />;
  }

  return (
    <AuthContext.Provider value={{ ...authState, handleLogin, handleBiometric, handleOAuth, handleLogout }}>
      <Stack.Navigator>
        <Stack.Screen name="Login" component={LoginScreen} />
        <Stack.Screen name="Signup" component={SignupScreen} />
        <Stack.Screen name="ForgotPassword" component={ForgotPasswordScreen} />
      </Stack.Navigator>
    </AuthContext.Provider>
  );
};
```

When to use: Every mobile app requiring user authentication, multi-factor security.

Customization points:
- Add `2FA` verification screen before success
- Add `passwordless` flow (magic links, OTP)
- Implement `session` timeout with re-authentication prompt
- Add biometric fallback chain (Face ID → Touch ID → password)

---

## 5. Repository Pattern Template

### React Native + Redux (Local + Remote Sources)

```typescript
// src/features/posts/repository.ts
// TODO: Customize cache duration and retry logic

interface Post {
  id: string;
  title: string;
  content: string;
  createdAt: string;
}

interface CacheEntry<T> {
  data: T;
  timestamp: number;
}

class PostRepository {
  private cache: Map<string, CacheEntry<Post[]>> = new Map();
  private readonly CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

  async getPosts(options: { forceRefresh?: boolean } = {}): Promise<Post[]> {
    // Check cache first
    if (!options.forceRefresh) {
      const cached = this.getFromCache('posts');
      if (cached) return cached;
    }

    try {
      // Fetch from remote
      const posts = await apiClient.get<Post[]>('/posts');
      this.setCache('posts', posts);
      return posts;
    } catch (error) {
      // Fallback to cache on error
      const cached = this.getFromCache('posts', true);
      if (cached) return cached;
      throw error;
    }
  }

  async createPost(data: Omit<Post, 'id' | 'createdAt'>): Promise<Post> {
    const newPost = await apiClient.post<Post>('/posts', data);
    this.invalidateCache('posts');
    return newPost;
  }

  async updatePost(id: string, data: Partial<Post>): Promise<Post> {
    const updated = await apiClient.put<Post>(`/posts/${id}`, data);
    this.invalidateCache('posts');
    return updated;
  }

  private getFromCache(key: string, ignoreExpiry = false): Post[] | null {
    const entry = this.cache.get(key);
    if (!entry) return null;

    const isExpired = Date.now() - entry.timestamp > this.CACHE_DURATION;
    if (isExpired && !ignoreExpiry) return null;

    return entry.data;
  }

  private setCache(key: string, data: Post[]): void {
    this.cache.set(key, { data, timestamp: Date.now() });
  }

  private invalidateCache(key: string): void {
    this.cache.delete(key);
  }
}

export const postRepository = new PostRepository();
```

When to use: Managing data from APIs and local storage, implementing offline-first behavior.

Customization points:
- Replace `Map` with SQLite (local persistence)
- Add `pagination` tracking to cache
- Implement `optimistic` updates before server confirmation
- Add `conflict` resolution for sync scenarios

---

## 6. List/Feed Screen Template

### React Native (Pagination + Pull-to-Refresh)

```typescript
// src/features/posts/screens/PostListScreen.tsx
// TODO: Customize page size and empty/error states

const PostListScreen: React.FC = () => {
  const [posts, setPosts] = useState<Post[]>([]);
  const [page, setPage] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  const PAGE_SIZE = 20; // TODO: Customize

  useEffect(() => {
    loadInitialPosts();
  }, []);

  const loadInitialPosts = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await postRepository.getPosts({ page: 1, limit: PAGE_SIZE });
      setPosts(response.data);
      setHasMore(response.hasMore);
      setPage(1);
    } catch (err) {
      setError('Failed to load posts. Pull to retry.');
    } finally {
      setIsLoading(false);
    }
  };

  const loadMorePosts = async () => {
    if (!hasMore || isLoading) return;
    try {
      const nextPage = page + 1;
      const response = await postRepository.getPosts({
        page: nextPage,
        limit: PAGE_SIZE
      });
      setPosts([...posts, ...response.data]);
      setHasMore(response.hasMore);
      setPage(nextPage);
    } catch (err) {
      setError('Failed to load more posts.');
    }
  };

  const handleRefresh = async () => {
    try {
      setIsRefreshing(true);
      setError(null);
      const response = await postRepository.getPosts({
        forceRefresh: true,
        page: 1,
        limit: PAGE_SIZE
      });
      setPosts(response.data);
      setPage(1);
      setHasMore(response.hasMore);
    } catch (err) {
      setError('Failed to refresh posts.');
    } finally {
      setIsRefreshing(false);
    }
  };

  const filteredPosts = posts.filter(post =>
    post.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (isLoading && posts.length === 0) {
    return <LoadingState />;
  }

  if (error && posts.length === 0) {
    return (
      <ErrorState
        message={error}
        onRetry={loadInitialPosts}
      />
    );
  }

  return (
    <FlatList
      data={filteredPosts}
      renderItem={({ item }) => <PostCard post={item} />}
      keyExtractor={item => item.id}
      ListHeaderComponent={
        <SearchBar
          value={searchQuery}
          onChangeText={setSearchQuery}
          placeholder="Search posts..."
        />
      }
      ListEmptyComponent={<EmptyState />}
      ListFooterComponent={
        hasMore ? <LoadingIndicator /> : null
      }
      onEndReached={loadMorePosts}
      onEndReachedThreshold={0.5}
      refreshing={isRefreshing}
      onRefresh={handleRefresh}
    />
  );
};
```

When to use: Social feeds, infinite lists, product catalogs, any scrollable content.

Customization points:
- Add `category filters` with multiple selections
- Add `sort options` (newest, popular, trending)
- Implement `skeleton loading` during initial load
- Add `sticky header` for filters/search
- Implement `haptic feedback` on pull-to-refresh

---

## 7. Form Screen Template

### React Native (Validation + Submission)

```typescript
// src/features/profile/screens/EditProfileScreen.tsx
// TODO: Customize validation rules and API endpoint

interface FormData {
  firstName: string;
  lastName: string;
  email: string;
  bio: string;
}

const EditProfileScreen: React.FC = () => {
  const [formData, setFormData] = useState<FormData>(initialData);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [touched, setTouched] = useState<Record<string, boolean>>({});

  const validateField = (name: keyof FormData, value: string): string => {
    // TODO: Customize validation rules
    switch (name) {
      case 'firstName':
      case 'lastName':
        return value.trim().length < 2 ? 'Name must be at least 2 characters' : '';
      case 'email':
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value) ? '' : 'Invalid email';
      case 'bio':
        return value.length > 500 ? 'Bio must be under 500 characters' : '';
      default:
        return '';
    }
  };

  const handleChange = (name: keyof FormData, value: string) => {
    setFormData(prev => ({ ...prev, [name]: value }));
    if (touched[name]) {
      const error = validateField(name, value);
      setErrors(prev => ({ ...prev, [name]: error }));
    }
  };

  const handleBlur = (name: keyof FormData) => {
    setTouched(prev => ({ ...prev, [name]: true }));
    const error = validateField(name, formData[name]);
    setErrors(prev => ({ ...prev, [name]: error }));
  };

  const handleSubmit = async () => {
    // Validate all fields
    const newErrors: Record<string, string> = {};
    Object.keys(formData).forEach(key => {
      const error = validateField(key as keyof FormData, formData[key as keyof FormData]);
      if (error) newErrors[key] = error;
    });

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    try {
      setIsSubmitting(true);
      setSubmitError(null);
      await userApi.updateProfile(formData);
      // TODO: Show success toast/navigate back
      navigation.goBack();
    } catch (error) {
      setSubmitError(error instanceof Error ? error.message : 'Update failed');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <KeyboardAvoidingView behavior="padding" style={styles.container}>
      <ScrollView showsVerticalScrollIndicator={false}>
        <TextField
          label="First Name"
          value={formData.firstName}
          onChangeText={(value) => handleChange('firstName', value)}
          onBlur={() => handleBlur('firstName')}
          error={touched.firstName ? errors.firstName : ''}
          placeholder="Enter first name"
        />

        <TextField
          label="Last Name"
          value={formData.lastName}
          onChangeText={(value) => handleChange('lastName', value)}
          onBlur={() => handleBlur('lastName')}
          error={touched.lastName ? errors.lastName : ''}
          placeholder="Enter last name"
        />

        <TextField
          label="Email"
          value={formData.email}
          onChangeText={(value) => handleChange('email', value)}
          onBlur={() => handleBlur('email')}
          error={touched.email ? errors.email : ''}
          placeholder="Enter email"
          keyboardType="email-address"
        />

        <TextField
          label="Bio"
          value={formData.bio}
          onChangeText={(value) => handleChange('bio', value)}
          onBlur={() => handleBlur('bio')}
          error={touched.bio ? errors.bio : ''}
          placeholder="Tell us about yourself"
          multiline
          maxLength={500}
        />

        {submitError && (
          <ErrorBanner message={submitError} />
        )}

        <Button
          label="Save Changes"
          onPress={handleSubmit}
          isLoading={isSubmitting}
          disabled={isSubmitting}
        />
      </ScrollView>
    </KeyboardAvoidingView>
  );
};
```

When to use: User profiles, settings, checkout, any data entry requiring validation.

Customization points:
- Add `field dependencies` (state affects validation of other fields)
- Implement `debounced` async validation (email availability check)
- Add `conditional fields` (show based on previous selections)
- Add `autofill` from contacts or camera
- Implement `draft saving` to local storage

---

## 8. Settings Screen Template

### React Native (Grouped Settings with State Management)

```typescript
// src/features/settings/screens/SettingsScreen.tsx
// TODO: Customize settings groups and toggle handlers

const SettingsScreen: React.FC = () => {
  const { user, updateSettings } = useAuth();
  const [settings, setSettings] = useState(user.settings);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const handleThemeToggle = async (enabled: boolean) => {
    try {
      setIsDarkMode(enabled);
      await updateSettings({ isDarkMode: enabled });
      // Update app theme
    } catch (error) {
      setIsDarkMode(!enabled); // Revert on error
    }
  };

  const handleNotificationToggle = async (key: string, enabled: boolean) => {
    try {
      await updateSettings({
        notifications: {
          ...settings.notifications,
          [key]: enabled
        }
      });
      setSettings(prev => ({
        ...prev,
        notifications: { ...prev.notifications, [key]: enabled }
      }));
    } catch (error) {
      showErrorToast('Failed to update notification settings');
    }
  };

  const handleLogout = async () => {
    try {
      setIsSaving(true);
      await authService.logout();
      // Navigate to auth screen
    } catch (error) {
      showErrorToast('Logout failed');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      {/* Account Section */}
      <SettingsSection title="Account">
        <SettingsRow
          icon="person"
          label="Profile"
          onPress={() => navigation.navigate('EditProfile')}
        />
        <SettingsRow
          icon="lock"
          label="Password"
          onPress={() => navigation.navigate('ChangePassword')}
        />
        <SettingsRow
          icon="bell"
          label="Email"
          value={user.email}
          onPress={() => navigation.navigate('ChangeEmail')}
        />
      </SettingsSection>

      {/* Notifications Section */}
      <SettingsSection title="Notifications">
        <SettingsToggle
          icon="mail"
          label="Email Notifications"
          value={settings.notifications?.email ?? true}
          onValueChange={(enabled) => handleNotificationToggle('email', enabled)}
        />
        <SettingsToggle
          icon="smartphone"
          label="Push Notifications"
          value={settings.notifications?.push ?? true}
          onValueChange={(enabled) => handleNotificationToggle('push', enabled)}
        />
        <SettingsToggle
          icon="message"
          label="SMS Notifications"
          value={settings.notifications?.sms ?? false}
          onValueChange={(enabled) => handleNotificationToggle('sms', enabled)}
        />
      </SettingsSection>

      {/* Display Section */}
      <SettingsSection title="Display">
        <SettingsToggle
          icon="moon"
          label="Dark Mode"
          value={isDarkMode}
          onValueChange={handleThemeToggle}
        />
        <SettingsPicker
          icon="textformat"
          label="Text Size"
          value={settings.textSize ?? 'medium'}
          options={['small', 'medium', 'large']}
          onValueChange={(size) => updateSettings({ textSize: size })}
        />
      </SettingsSection>

      {/* Privacy Section */}
      <SettingsSection title="Privacy & Security">
        <SettingsToggle
          icon="eye"
          label="Show Online Status"
          value={settings.showOnlineStatus ?? true}
          onValueChange={(enabled) => updateSettings({ showOnlineStatus: enabled })}
        />
        <SettingsRow
          icon="lock"
          label="Block List"
          onPress={() => navigation.navigate('BlockedUsers')}
        />
        <SettingsRow
          icon="document"
          label="Privacy Policy"
          onPress={() => openURL('https://example.com/privacy')}
        />
      </SettingsSection>

      {/* Danger Zone */}
      <SettingsSection title="Account Actions">
        <SettingsButton
          label="Logout"
          onPress={handleLogout}
          isLoading={isSaving}
          style={styles.logoutButton}
          textStyle={styles.logoutText}
        />
        <SettingsButton
          label="Delete Account"
          onPress={() => showDeleteConfirmation()}
          style={styles.dangerButton}
          textStyle={styles.dangerText}
        />
      </SettingsSection>
    </ScrollView>
  );
};
```

When to use: All apps with user preferences, feature toggles, account management.

Customization points:
- Add `language selection` with locale switching
- Add `biometric authentication` toggle
- Add `data export/import` functionality
- Add `version info` and `about` section
- Add `in-app feedback` form

---

## 9. Error Handling Pattern

### Typed Error Hierarchy (React Native)

```typescript
// src/shared/errors/AppError.ts
// TODO: Customize error codes and user messages

export enum ErrorCode {
  NETWORK_ERROR = 'NETWORK_ERROR',
  UNAUTHORIZED = 'UNAUTHORIZED',
  FORBIDDEN = 'FORBIDDEN',
  NOT_FOUND = 'NOT_FOUND',
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  SERVER_ERROR = 'SERVER_ERROR',
  UNKNOWN_ERROR = 'UNKNOWN_ERROR',
}

export class AppError extends Error {
  constructor(
    public code: ErrorCode,
    message: string,
    public statusCode?: number,
    public originalError?: Error
  ) {
    super(message);
    this.name = 'AppError';
  }

  isRetryable(): boolean {
    return [
      ErrorCode.NETWORK_ERROR,
      ErrorCode.SERVER_ERROR,
    ].includes(this.code);
  }

  getUserMessage(): string {
    // TODO: Customize user-facing messages
    const messages: Record<ErrorCode, string> = {
      [ErrorCode.NETWORK_ERROR]: 'Connection failed. Please check your internet.',
      [ErrorCode.UNAUTHORIZED]: 'Please log in again.',
      [ErrorCode.FORBIDDEN]: 'You don\'t have permission to do this.',
      [ErrorCode.NOT_FOUND]: 'Resource not found.',
      [ErrorCode.VALIDATION_ERROR]: 'Please check your input.',
      [ErrorCode.SERVER_ERROR]: 'Server error. Please try again later.',
      [ErrorCode.UNKNOWN_ERROR]: 'Something went wrong. Please try again.',
    };
    return messages[this.code] || this.message;
  }
}

// src/shared/errors/errorBoundary.tsx
interface ErrorBoundaryProps {
  children: React.ReactNode;
  onError?: (error: Error) => void;
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps> {
  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error boundary caught:', error, errorInfo);
    this.props.onError?.(error);
  }

  render() {
    return this.props.children;
  }
}

// src/shared/errors/errorHandler.ts
export const handleApiError = (error: unknown): AppError => {
  if (error instanceof AppError) return error;

  if (axios.isAxiosError(error)) {
    const status = error.response?.status;
    const code = mapHttpStatusToErrorCode(status);
    return new AppError(code, error.message, status, error);
  }

  if (error instanceof Error) {
    return new AppError(ErrorCode.UNKNOWN_ERROR, error.message, undefined, error);
  }

  return new AppError(ErrorCode.UNKNOWN_ERROR, 'An unknown error occurred');
};

const mapHttpStatusToErrorCode = (status?: number): ErrorCode => {
  switch (status) {
    case 401: return ErrorCode.UNAUTHORIZED;
    case 403: return ErrorCode.FORBIDDEN;
    case 404: return ErrorCode.NOT_FOUND;
    case 400: return ErrorCode.VALIDATION_ERROR;
    case 500:
    case 502:
    case 503:
      return ErrorCode.SERVER_ERROR;
    default:
      return status && status >= 500 ? ErrorCode.SERVER_ERROR : ErrorCode.UNKNOWN_ERROR;
  }
};
```

When to use: Consistent error handling across app, user-facing error messages, retry logic.

Customization points:
- Add error `logging service` integration (Sentry, Crash lytics)
- Add `breadcrumb tracking` for debugging
- Add `error reporting` from users with reproduction steps
- Implement `offline error` differentiation

---

## 10. Navigation Setup Template

### React Native (Tab + Stack Navigator)

```typescript
// src/navigation/RootNavigator.tsx
// TODO: Customize tab icons, colors, and screen options

export type RootStackParamList = {
  Auth: undefined;
  App: undefined;
  Splash: undefined;
};

export type AppTabParamList = {
  Home: undefined;
  Explore: undefined;
  Messages: undefined;
  Profile: undefined;
};

export type HomeStackParamList = {
  HomeList: undefined;
  PostDetail: { postId: string };
  CreatePost: undefined;
};

const Splash = createNativeStackNavigator<RootStackParamList>();
const Auth = createNativeStackNavigator<RootStackParamList>();
const App = createBottomTabNavigator<AppTabParamList>();
const HomeStack = createNativeStackNavigator<HomeStackParamList>();

const HomeStackNavigator = () => (
  <HomeStack.Navigator
    screenOptions={{
      headerShown: true,
      headerStyle: { backgroundColor: colors.primary },
      headerTintColor: colors.white,
      headerTitleStyle: { fontWeight: '600' },
    }}
  >
    <HomeStack.Screen
      name="HomeList"
      component={HomeListScreen}
      options={{ title: 'Home' }}
    />
    <HomeStack.Screen
      name="PostDetail"
      component={PostDetailScreen}
      options={{ title: 'Post' }}
    />
    <HomeStack.Screen
      name="CreatePost"
      component={CreatePostScreen}
      options={{
        title: 'Create Post',
        presentation: 'modal'
      }}
    />
  </HomeStack.Navigator>
);

const AppNavigator = () => (
  <App.Navigator
    screenOptions={({ route }) => ({
      headerShown: false,
      tabBarIcon: ({ color, size }) => {
        // TODO: Customize icons per route
        const icons: Record<keyof AppTabParamList, string> = {
          Home: 'home',
          Explore: 'compass',
          Messages: 'mail',
          Profile: 'user',
        };
        return <Icon name={icons[route.name]} size={size} color={color} />;
      },
      tabBarActiveTintColor: colors.primary,
      tabBarInactiveTintColor: colors.gray,
    })}
  >
    <App.Screen
      name="Home"
      component={HomeStackNavigator}
      options={{ title: 'Home' }}
    />
    <App.Screen
      name="Explore"
      component={ExploreScreen}
      options={{ title: 'Explore' }}
    />
    <App.Screen
      name="Messages"
      component={MessagesScreen}
      options={{ title: 'Messages' }}
    />
    <App.Screen
      name="Profile"
      component={ProfileScreen}
      options={{ title: 'Profile' }}
    />
  </App.Navigator>
);

const AuthNavigator = () => (
  <Auth.Navigator screenOptions={{ headerShown: false }}>
    <Auth.Screen name="Auth" component={AuthStack} />
  </Auth.Navigator>
);

export const RootNavigator = () => {
  const { isLoading, isSignedIn } = useAuth();

  if (isLoading) {
    return (
      <Splash.Navigator>
        <Splash.Screen
          name="Splash"
          component={SplashScreen}
          options={{ animationEnabled: false }}
        />
      </Splash.Navigator>
    );
  }

  return (
    <Splash.Navigator>
      {isSignedIn ? (
        <Splash.Screen
          name="App"
          component={AppNavigator}
          options={{ animationEnabled: false }}
        />
      ) : (
        <Splash.Screen
          name="Auth"
          component={AuthNavigator}
          options={{ animationEnabled: false }}
        />
      )}
    </Splash.Navigator>
  );
};
```

When to use: Every mobile app, foundation of navigation structure.

Customization points:
- Add `deep linking` support for external URLs
- Add `bottom sheet` navigation for modals
- Add `drawer navigation` for side menu
- Implement `route-based permissions` checks
- Add `transition animations` between screens

---

## Quick Reference: Framework Selection Guide

| Framework | Best For | Setup Complexity |
|-----------|----------|------------------|
| **React Native/Expo** | Cross-platform, fast iteration, large team | Medium |
| **Flutter** | Cross-platform, native performance, Dart preference | Medium-High |
| **SwiftUI** | iOS-only, latest iOS features, Apple ecosystem | Medium |
| **Jetpack Compose** | Android-only, Material 3, Kotlin preference | Medium-High |

---

## Best Practices Across All Templates

1. **Type Safety**: Use TypeScript/Kotlin/Swift strictly typed, avoid `any`
2. **Testing**: Unit test business logic, integration test screens, E2E test critical flows
3. **Performance**: Implement memoization, lazy loading, list virtualization
4. **Accessibility**: WCAG 2.1 AA minimum, semantic labels, sufficient color contrast
5. **Error Handling**: Never silent failures, always provide user feedback
6. **Security**: Never log sensitive data, use secure storage for tokens, validate all inputs
7. **State Management**: Keep state as close to where it's used, lift only when necessary
8. **Code Organization**: One responsibility per file/class, 200-300 line max file size
