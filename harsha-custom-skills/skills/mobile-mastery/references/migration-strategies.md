# Mobile App Migration Strategies Reference

## Table of Contents

- [Overview](#overview)
- [1. React Native: Class → Functional Components (Hooks)](#1-react-native-class--functional-components-hooks)
- [2. React Native: Old Arch → New Architecture](#2-react-native-old-arch--new-architecture)
- [3. iOS: UIKit → SwiftUI](#3-ios-uikit--swiftui)
- [4. Android: Views → Jetpack Compose](#4-android-views--jetpack-compose)
- [5. Cordova → Capacitor Migration](#5-cordova--capacitor-migration)
- [6. React Native ↔ Flutter Migration](#6-react-native--flutter-migration)
- [7. Native → Cross-Platform (Strategic Decision)](#7-native--cross-platform-strategic-decision)
- [8. Major Version Upgrades](#8-major-version-upgrades)
- [9. Monolith → Modular Architecture](#9-monolith--modular-architecture)
- [10. REST → GraphQL Migration](#10-rest--graphql-migration)
- [11. State Management Migration](#11-state-management-migration)
- [12. Database Migration](#12-database-migration)
- [Decision Criteria Framework](#decision-criteria-framework)
- [Quick Reference: Timeline & Risk Summary](#quick-reference-timeline--risk-summary)
- [References & Tools](#references--tools)

## Overview
Mobile app migrations span multiple dimensions: architecture, frameworks, languages, and platforms. This guide covers decision criteria, risk assessment, and step-by-step approaches for common migration scenarios.

---

## 1. React Native: Class → Functional Components (Hooks)

### Decision Criteria
- **Migrate if**: Team uses modern React practices, needs better code organization, targeting RN 0.60+
- **Risk Level**: Low for new features, Medium for existing components
- **Time Estimate**: 1-2 weeks per 100 components

### Step-by-Step Migration

```javascript
// BEFORE: Class Component
class UserProfile extends Component {
  constructor(props) {
    super(props);
    this.state = { user: null, loading: true };
  }

  componentDidMount() {
    fetchUser().then(user => this.setState({ user, loading: false }));
  }

  componentDidUpdate(prevProps) {
    if (prevProps.userId !== this.props.userId) {
      this.setState({ loading: true });
      fetchUser(this.props.userId).then(user => this.setState({ user, loading: false }));
    }
  }

  render() {
    const { user, loading } = this.state;
    return loading ? <Loader /> : <ProfileView user={user} />;
  }
}

// AFTER: Functional Component with Hooks
const UserProfile = ({ userId }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetchUser(userId).then(user => {
      setUser(user);
      setLoading(false);
    });
  }, [userId]);

  return loading ? <Loader /> : <ProfileView user={user} />;
};
```

### HOC to Hooks Pattern
```javascript
// Replace withUser HOC
function withUser(Component) {
  return (props) => {
    const user = useUser();
    return <Component user={user} {...props} />;
  };
}

// Replace connect() from Redux
const mapStateToProps = state => ({ user: state.user });
// Becomes:
const user = useSelector(state => state.user);
```

### Incremental Adoption Strategy
1. **Freeze classs**: Stop creating new class components
2. **Extract selectively**: Convert 10% of smallest components first
3. **Verify behavior**: Run E2E tests for each converted component
4. **Build confidence**: Convert feature-related components as a batch
5. **Cleanup**: Remove unused lifecycle methods from remaining classes

---

## 2. React Native: Old Arch → New Architecture

### Decision Criteria
- **Migrate if**: Performance-critical features, need better interop, upgrading RN 0.73+
- **Risk Level**: High—requires native code changes
- **Time Estimate**: 4-8 weeks per module

### Core Components

**Fabric**: New rendering engine replacing React Shadow Tree
- Reduced bridge traffic, synchronous layout
- Enable per-component: `fabricEnabled: true` in codebase.json

**TurboModules**: Type-safe native modules replacing legacy bridge
- Auto-generated TypeScript specs
- Can coexist with legacy modules during transition

**JSI (JavaScript Interface)**: Direct access to native objects
- Synchronous calls—use sparingly
- Perfect for crypto, image processing

### Migration Path
```javascript
// Step 1: Generate TurboModule spec (TypeScript)
export interface Spec {
  add(a: number, b: number): Promise<number>;
  getCurrentTimestamp(): number;
}

// Step 2: Implement native (Swift)
@objc(Calculator)
class Calculator: NSObject {
  @objc func add(_ a: NSNumber, _ b: NSNumber, resolve: @escaping RCTPromiseResolveBlock, reject: @escaping RCTPromiseRejectBlock) {
    resolve(NSNumber(value: a.doubleValue + b.doubleValue))
  }

  @objc func getCurrentTimestamp() -> NSNumber {
    return NSNumber(value: Date().timeIntervalSince1970)
  }
}

// Step 3: Use from JS
import { NativeModules } from 'react-native';
const { Calculator } = NativeModules;
const result = await Calculator.add(5, 3); // Promise
const timestamp = Calculator.getCurrentTimestamp(); // Sync
```

### Codegen Setup
```javascript
// package.json
"codegenConfig": {
  "libraries": [
    {
      "name": "MyModule",
      "type": "all",
      "jsSrcsDir": "js/specs"
    }
  ]
}
```

### Incremental Adoption
1. **Enable bridgeless mode**: `bridgelessEnabled: true` in RN config (experimental)
2. **Convert high-traffic modules first**: Analytics, auth, payments
3. **Keep legacy bridge**: Both architectures work in parallel
4. **Test on RC**: Use release candidates before stable
5. **Monitor native crash rates**: Bridge removal often exposes edge cases

---

## 3. iOS: UIKit → SwiftUI

### Decision Criteria
- **Migrate if**: iOS 14+, need modern UI, building new features
- **Risk Level**: Low for new screens, High for core navigation
- **Time Estimate**: 3 weeks per major screen

### Incremental Integration

**UIHostingController**: Embed SwiftUI in UIKit
```swift
// Existing UIViewController
class UserListViewController: UIViewController {
  override func viewDidLoad() {
    super.viewDidLoad()

    // Add SwiftUI view
    let swiftUIView = UserListSwiftUI()
    let hostingController = UIHostingController(rootView: swiftUIView)
    addChild(hostingController)
    view.addSubview(hostingController.view)
    hostingController.didMove(toParent: self)
  }
}

// SwiftUI view
struct UserListSwiftUI: View {
  @StateObject var viewModel = UserListViewModel()

  var body: some View {
    List(viewModel.users, id: \.id) { user in
      Text(user.name)
    }
  }
}
```

**UIViewRepresentable**: Embed UIKit in SwiftUI
```swift
struct LegacyMapView: UIViewRepresentable {
  func makeUIView(context: Context) -> MKMapView {
    MKMapView()
  }

  func updateUIView(_ uiView: MKMapView, context: Context) {
    // Sync SwiftUI state → UIKit
  }
}
```

### View Model Sharing
```swift
// Shared between UIKit and SwiftUI
class UserViewModel: ObservableObject {
  @Published var user: User?

  func loadUser(id: String) async {
    self.user = await userService.getUser(id)
  }
}

// UIKit usage
let viewModel = UserViewModel()
viewModel.loadUser(id: "123")

// SwiftUI usage
@StateObject var viewModel = UserViewModel()
```

### Navigation Migration Strategy
1. **Separate concerns**: Navigation logic from UI
2. **Adopt NavigationStack**: SwiftUI 4.0+ (iOS 16+)
3. **Hybrid approach**: UINavigationController for legacy, NavigationStack for new
4. **Coordinator pattern**: Manage transitions in both systems

---

## 4. Android: Views → Jetpack Compose

### Decision Criteria
- **Migrate if**: Targeting API 30+, complex UI logic, performance critical
- **Risk Level**: Medium—Compose matures with each release
- **Time Estimate**: 2-4 weeks per screen

### ComposeView in XML Layout
```xml
<!-- activity_user.xml -->
<LinearLayout>
  <ComposeView
    android:id="@+id/compose_header"
    android:layout_width="match_parent"
    android:layout_height="wrap_content" />
  <RecyclerView
    android:id="@+id/legacy_list" />
</LinearLayout>
```

```kotlin
// Activity
val composeView: ComposeView = binding.composeHeader
composeView.setContent {
  UserHeader(viewModel = viewModel)
}
```

### AndroidView in Compose
```kotlin
@Composable
fun MapScreen(viewModel: MapViewModel) {
  Column {
    AndroidView(
      factory = { context -> MapView(context) },
      modifier = Modifier.fillMaxWidth().height(300.dp),
      update = { mapView ->
        mapView.getMapAsync { googleMap ->
          // Update legacy component
        }
      }
    )
    ComposeContent()
  }
}
```

### Shared ViewModel Pattern
```kotlin
// Shared ViewModel (Compose + Views)
class OrderViewModel : ViewModel() {
  val orders: StateFlow<List<Order>> = _orders.asStateFlow()
  private val _orders = MutableStateFlow(emptyList<Order>())

  fun loadOrders() { /* ... */ }
}

// Activity using both
val viewModel: OrderViewModel = viewModel()

val composeView: ComposeView = binding.header
composeView.setContent {
  val orders by viewModel.orders.collectAsState()
  OrderHeader(count = orders.size)
}

val recyclerView: RecyclerView = binding.list
val adapter = OrderAdapter(viewModel)
recyclerView.adapter = adapter
```

### Screen-by-Screen Migration Plan
1. **Start with isolated screens**: No navigation dependencies
2. **Replace one layout at a time**: ComposeView incrementally
3. **Migrate logic to ViewModel**: Decouple from Activity
4. **Test with different configurations**: Dark mode, languages
5. **Profile performance**: Use Compose Layout Inspector

---

## 5. Cordova → Capacitor Migration

### Decision Criteria
- **Migrate if**: Cord va 10+, need modern plugin ecosystem, better native integration
- **Risk Level**: Medium—similar concepts, different APIs
- **Time Estimate**: 2-3 weeks for typical app

### Plugin Migration Map
```javascript
// Cordova plugins → Capacitor equivalents
cordova-plugin-camera → @capacitor/camera
cordova-plugin-geolocation → @capacitor/geolocation
cordova-plugin-statusbar → @capacitor/status-bar
cordova-plugin-sqlite → @capacitor/sqlite
cordova-plugin-http → @capacitor/http (or fetch API)

// Custom plugins need rewriting—no Cordova compatibility layer
```

### WebView & Permissions Differences
```javascript
// Cordova: Implicit permissions via cordova.yaml
// Capacitor: Explicit Android permissions & iOS Info.plist

// capacitor.config.json
{
  "plugins": {
    "Camera": {
      "permissions": ["camera", "photos"]
    },
    "Geolocation": {
      "permissions": ["location"]
    }
  }
}
```

### Step-by-Step Migration
```bash
# 1. Create Capacitor project
npm install @capacitor/core @capacitor/cli
npx cap init MyApp com.example.myapp

# 2. Copy web assets
cp -r www/src/* src/

# 3. Add platforms
npx cap add android
npx cap add ios

# 4. Migrate Cordova plugins one-by-one
npm uninstall cordova-plugin-camera
npm install @capacitor/camera

# 5. Update JavaScript code
// OLD: navigator.camera.getPicture()
// NEW: Camera.getPhoto()
import { Camera } from '@capacitor/camera';
const photo = await Camera.getPhoto();

# 6. Sync & test on device
npx cap sync
npx cap open android
npx cap open ios
```

### Native Project Access
```javascript
// Capacitor: Direct Xcode/Android Studio project access
// Build production: npx cap copy && open ios/App/App.xcworkspace
// Native modules: Modify Swift/Kotlin directly in platform folders

// Example: Custom Swift plugin
// ios/App/App/CustomPlugin.swift
@objc(CustomPlugin)
class CustomPlugin : CAPPlugin {
  @objc func customMethod(_ call: CAPPluginCall) {
    call.resolve(["result": "success"])
  }
}
```

---

## 6. React Native ↔ Flutter Migration

### Decision Criteria
- **Migrate if**: Performance critical, team expertise aligns, rebuilding feature set acceptable
- **Risk Level**: Very High—complete rewrite
- **Time Estimate**: 3-6 months depending on app complexity

### When to Consider
- **RN → Flutter**: Complex animations, real-time apps, Dart skill available
- **Flutter → RN**: JavaScript ecosystem dependency, web support critical
- **Neither**: Cross-platform bridges (KMP, React + native) often better

### Gradual Approach via Platform Channels
```dart
// Flutter: Call shared backend API
class AuthService {
  final platform = MethodChannel('com.example.app/auth');

  Future<String> getToken() async {
    final token = await platform.invokeMethod('getToken');
    return token;
  }
}

// Kotlin: Implement shared authentication
class MainActivity: FlutterActivity() {
  override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
    MethodChannel(flutterEngine.dartExecutor.binaryMessenger, "com.example.app/auth")
      .setMethodCallHandler { call, result ->
        when(call.method) {
          "getToken" -> result.success(getToken())
        }
      }
  }
}
```

### Shared Backend Strategy
- Keep API layer identical: REST/GraphQL endpoints unchanged
- Migrate one platform at a time: RN core → Flutter UI
- Share data models: Generate from OpenAPI/protobuf
- Maintain feature parity: Both platforms get same backend

---

## 7. Native → Cross-Platform (Strategic Decision)

### Evaluation Framework
| Factor | Keep Native | Cross-Platform | Hybrid |
|--------|-----------|------------------|--------|
| Code reuse | 0% | 60-80% | 40-60% |
| Performance | Optimal | Good (95%) | Good |
| Time to market | Slow | Fast | Fast |
| Team size | Large | Small-Medium | Small-Medium |

### Kotlin Multiplatform (KMP) as Bridge
```kotlin
// Shared business logic (Kotlin Multiplatform)
// common/src/commonMain/kotlin/AuthService.kt
expect class AuthService {
  suspend fun login(email: String, password: String): User
}

// Android implementation
// android/src/androidMain/kotlin/AuthService.kt
actual class AuthService {
  actual suspend fun login(email: String, password: String) = // impl
}

// iOS implementation (generated Swift interface)
// Autogenerated Swift interop for native iOS app
let authService = AuthService()
let user = try await authService.login(email: "test@example.com", password: "123")
```

### What to Share
- Business logic, auth, encryption
- Data models, API clients
- Validation, formatting utilities

### What to Keep Native
- UI (platform-specific design systems)
- Gesture handlers
- Platform-specific services (notifications, in-app purchase)

---

## 8. Major Version Upgrades

### React Native Version Bumps

**Using Upgrade Helper**
```bash
# Visit upgrade-helper.vercel.app to see full diff
# Example: RN 0.72 → 0.73 changes
npx react-native upgrade

# Manual process
npm install react-native@latest
npm install
npx pod-install
npx react-native doctor
```

**Breaking Changes to Watch**
```javascript
// RN 0.73: Removed deprecated Animated APIs
// OLD: Animated.createAnimatedComponent()
// NEW: React.forwardRef() + useAnimatedStyle()

// RN 0.74: New JSI-based modules required
// Migrate TurboModule specs to TypeScript

// RN 0.75: Removed legacy bridge (if bridgeless enabled)
```

### Flutter Version Channels
```bash
# Stable: Production-ready
flutter channel stable && flutter upgrade

# Beta: Latest features, few bugs (monthly)
flutter channel beta && flutter upgrade

# Dev: Cutting edge, breaking changes frequent
flutter channel dev && flutter upgrade

# Version-specific features
flutter --version # Check current
flutter upgrade --build-example # Rebuild examples
```

### Xcode & SDK Version Requirements
```bash
# iOS deployment target increase
# iOS 13 → iOS 14 often required for new RN versions
# Update Podfile
platform :ios, '14.0'

# macOS version requirement
# Check with: system_profiler SPSoftwareDataType

# Xcode version
# RN 0.73+ requires Xcode 15+
xcode-select --install
```

### Gradle & AGP Upgrades
```gradle
// build.gradle (Project)
buildscript {
  ext {
    buildToolsVersion = "34.0.0" // Increase with AGP
    minSdkVersion = 24 // Often needs bump
    compileSdkVersion = 34
    targetSdkVersion = 34
  }

  dependencies {
    classpath 'com.android.tools.build:gradle:8.2.0' // AGP 8.2.0
  }
}

// gradle/wrapper/gradle-wrapper.properties
distributionUrl=https://services.gradle.org/distributions/gradle-8.4-all.zip
```

### Dependency Compatibility
```bash
# Before upgrade: Check compatibility
npm outdated
gem outdated (for iOS)
./gradlew dependencyUpdates (for Android)

# Lock file strategy
npm ci # Use lock file, prevents breaking changes
yarn install --frozen-lockfile
```

---

## 9. Monolith → Modular Architecture

### Decision Criteria
- **Migrate if**: App >50K LOC, multiple teams, slow build times (>5 min)
- **Risk Level**: High—complex dependency management
- **Time Estimate**: 2-3 weeks per feature module

### Feature Module Extraction
```
Before:
app/
  src/
    users/
    orders/
    payments/
    ui/
    data/

After:
app/ (core app shell)
feature-users/ (independent module)
feature-orders/ (independent module)
feature-payments/ (independent module)
shared-data/ (reusable data layer)
shared-ui/ (design system)
```

### Gradle Configuration
```gradle
// settings.gradle
include ':app'
include ':feature:users'
include ':feature:orders'
include ':shared:data'
include ':shared:ui'

// app/build.gradle (only depends on features)
dependencies {
  implementation project(':feature:users')
  implementation project(':feature:orders')
  implementation project(':shared:data')
}

// feature/users/build.gradle (depends on shared only)
dependencies {
  implementation project(':shared:data')
  implementation project(':shared:ui')
  // NO dependency on :feature:orders ← Clean!
}
```

### Build Time Optimization
```gradle
// Enable parallel builds
org.gradle.parallel=true
org.gradle.workers.max=8

// On-demand module loading (if using Gradle plugins)
org.gradle.plugins.internal.dynamic=true

// Cache remote builds
org.gradle.build.cache=true
```

### Dependency Graph Cleanup
```bash
# Identify circular dependencies
./gradlew projectDependencyDot | dot -Tpng -o deps.png

# Enforce architecture with Lint
// lint.xml
<issue id="ModuleUseWildcard" severity="error" />
```

### Incremental Modularization
1. **Phase 1**: Extract data layer (repositories, API clients)
2. **Phase 2**: Extract shared UI components
3. **Phase 3**: Extract feature modules (one major feature at a time)
4. **Phase 4**: Dynamic delivery (optional, advanced)

---

## 10. REST → GraphQL Migration

### Decision Criteria
- **Migrate if**: Overfetching/underfetching problems, real-time needs, mobile bandwidth concerns
- **Risk Level**: Medium—requires backend coordination
- **Time Estimate**: 4-6 weeks

### Adding GraphQL Alongside REST
```javascript
// Phase 1: GraphQL coexists with REST
// App still uses REST for 80% of queries
// New features use GraphQL (20%)

import { ApolloClient, gql, useQuery } from '@apollo/client';

const USER_QUERY = gql`
  query GetUser($id: ID!) {
    user(id: $id) {
      id
      name
      email
      posts(limit: 10) {
        id
        title
      }
    }
  }
`;

export function UserProfile({ userId }) {
  const { data, loading } = useQuery(USER_QUERY, {
    variables: { id: userId }
  });

  return <ProfileView user={data?.user} />;
}
```

### Incremental Endpoint Migration
```javascript
// Step-by-step plan
// Week 1: Simple queries (fetch single resource)
// Week 2: Complex queries (nested relationships)
// Week 3: Mutations (create, update, delete)
// Week 4: Subscriptions (real-time data)
// Week 5: Batch processing & optimization

// Apollo Code Generation (TypeScript support)
// codegen.yml
schema: 'https://api.example.com/graphql'
documents: 'src/**/*.graphql'
generates:
  src/generated/graphql.ts:
    plugins:
      - typescript
      - typescript-operations
```

### Schema Design for Mobile
```graphql
# Query sizes explicitly
type User {
  id: ID!
  name: String!
  email: String!

  # Mobile: Exclude by default
  profile: UserProfile
  settings: UserSettings
}

# Pagination for mobile
type Query {
  users(first: Int!, after: String): UserConnection!
}

type UserConnection {
  edges: [UserEdge!]!
  pageInfo: PageInfo!
}
```

### Caching Strategy Differences
```javascript
// REST: Simple HTTP caching
// GraphQL: Query-specific caching

// Apollo Client setup
const cache = new InMemoryCache({
  typePolicies: {
    User: {
      keyFields: ['id']
    }
  }
});

// Manual cache updates after mutation
const [updateUser] = useMutation(UPDATE_USER_MUTATION, {
  update(cache, { data: { updateUser } }) {
    cache.modify({
      fields: {
        user() {
          return updateUser;
        }
      }
    });
  }
});
```

---

## 11. State Management Migration

### Redux → Zustand
```javascript
// BEFORE: Redux
const initialState = { count: 0 };
const reducer = (state = initialState, action) => {
  switch(action.type) {
    case 'INCREMENT': return { count: state.count + 1 };
    default: return state;
  }
};
const store = createStore(reducer);

// AFTER: Zustand
import create from 'zustand';

const useCountStore = create(set => ({
  count: 0,
  increment: () => set(state => ({ count: state.count + 1 }))
}));

// Usage
function Counter() {
  const count = useCountStore(state => state.count);
  const increment = useCountStore(state => state.increment);
  return <button onClick={increment}>{count}</button>;
}
```

### Provider → Riverpod (Flutter)
```dart
// BEFORE: Provider
final counterProvider = StateNotifierProvider((ref) => CounterNotifier());

// AFTER: Riverpod (same API, better performance)
final counterProvider = StateNotifierProvider<CounterNotifier, int>((ref) {
  return CounterNotifier();
});

// Usage
class CounterPage extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final count = ref.watch(counterProvider);
    return FloatingActionButton(
      onPressed: () => ref.read(counterProvider.notifier).increment(),
      child: Text('$count')
    );
  }
}
```

### ViewModel Migration (Android)
```kotlin
// BEFORE: Presenter pattern
class UserPresenter(val view: UserView) {
  fun loadUser(id: String) {
    view.showLoading()
    userRepository.getUser(id) { user ->
      view.hideLoading()
      view.showUser(user)
    }
  }
}

// AFTER: ViewModel + LiveData
class UserViewModel : ViewModel() {
  val user: LiveData<User> = liveData {
    emit(userRepository.getUser(id))
  }
}

// Activity uses LiveData directly
viewModel.user.observe(this) { user ->
  updateUI(user)
}
```

### Incremental Adoption Without Breaking Code
```javascript
// Parallel operation during transition
const useUserState = () => {
  // Check new state manager first
  const newState = useZustandStore();

  // Fallback to Redux if not migrated yet
  const reduxState = useSelector(state => state.user);

  // Return whichever is available
  return newState || reduxState;
};
```

---

## 12. Database Migration

### SQLite → Room (Android)
```kotlin
// BEFORE: SQLite direct queries
val db = context.openOrCreateDatabase("app.db", MODE_PRIVATE, null)
val cursor = db.rawQuery("SELECT * FROM users WHERE id = ?", arrayOf(userId))

// AFTER: Room (type-safe, compile-time checked)
@Entity(tableName = "users")
data class User(
  @PrimaryKey val id: String,
  val name: String,
  val email: String
)

@Dao
interface UserDao {
  @Query("SELECT * FROM users WHERE id = :id")
  suspend fun getUser(id: String): User
}

@Database(entities = [User::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
  abstract fun userDao(): UserDao
}

// Usage
val database = Room.databaseBuilder(context, AppDatabase::class.java, "app.db").build()
val user = database.userDao().getUser(userId)
```

### Core Data → SwiftData
```swift
// BEFORE: Core Data
@NSManaged var name: String?
@NSManaged var email: String?

// AFTER: SwiftData (simpler, Swift-native)
@Model final class User {
  var name: String
  var email: String

  init(name: String, email: String) {
    self.name = name
    self.email = email
  }
}

// Usage
@Environment(\.modelContext) var context
func createUser(name: String, email: String) {
  let user = User(name: name, email: email)
  context.insert(user)
}
```

### Realm → SQLDelight (Kotlin Multiplatform)
```kotlin
// BEFORE: Realm
val users = realm.query<User>().find()

// AFTER: SQLDelight (SQL with type-safe API)
// sqldelight/users.sq
SELECT * FROM users WHERE id = ?;
selectById(id: String): User;

INSERT INTO users(id, name, email) VALUES(?, ?, ?);
insertUser;

// Usage
val queries = Database(driver).usersQueries
val user = queries.selectById(userId).executeAsOne()
queries.insertUser(id = "123", name = "John", email = "john@example.com")
```

### Schema Migration Strategies
```kotlin
// Room migration
val MIGRATION_1_2 = object : Migration(1, 2) {
  override fun migrate(database: SupportSQLiteDatabase) {
    // Add new column
    database.execSQL("ALTER TABLE users ADD COLUMN age INTEGER")
  }
}

val db = Room.databaseBuilder(context, AppDatabase::class.java, "app.db")
  .addMigrations(MIGRATION_1_2)
  .build()
```

### Data Migration Scripts
```bash
#!/bin/bash
# Migration script: users (SQLite) → Room (structured)

sqlite3 app.db "SELECT * FROM users;" | while read id name email; do
  # Transform and validate
  # Insert into new Room database
  adb shell am broadcast -a com.example.MIGRATE_USER \
    -e id "$id" -e name "$name" -e email "$email"
done
```

---

## Decision Criteria Framework

### Should We Migrate? (RICE Scoring)

**RICE = (Reach × Impact × Confidence) / Effort**

```
Reach: How many users affected (0-100)
Impact: Performance/quality gain (1=negligible, 3=major)
Confidence: Certainty of benefits (0-1)
Effort: Developer months required

Example:
- Migrate REST → GraphQL
  Reach: 100 (all users)
  Impact: 2 (moderate battery improvement)
  Confidence: 0.8
  Effort: 1.5 months
  RICE = (100 × 2 × 0.8) / 1.5 = 106.7 ✓ Worth it
```

### Risk Assessment Framework

| Risk Factor | Mitigation | Priority |
|------------|-----------|----------|
| Feature regression | E2E test coverage >80% | High |
| Performance | Profile before/after | High |
| Team knowledge | Training budget | Medium |
| Timeline | Buffer +50% estimate | High |
| Rollback plan | Feature flags, git branch | High |

### Go/No-Go Checklist
- [ ] Business value clearly defined
- [ ] Technical debt quantified
- [ ] Team has required skills
- [ ] Test coverage adequate (>70%)
- [ ] Rollback plan documented
- [ ] Stakeholder alignment on timeline
- [ ] Post-migration monitoring planned

---

## Quick Reference: Timeline & Risk Summary

| Migration | Difficulty | Time | Risk | Reward |
|-----------|-----------|------|------|--------|
| Class → Hooks | Low | 2w | Low | High |
| UIKit → SwiftUI | Medium | 3w | Med | High |
| Views → Compose | Medium | 2w | Med | High |
| Cordova → Capacitor | Medium | 2w | Med | High |
| Monolith → Modular | Hard | 6w | High | High |
| REST → GraphQL | Medium | 4w | Med | Med |
| RN → Flutter | Very Hard | 24w | Very High | Low (rewrite) |
| Redux → Zustand | Low | 1w | Low | Med |

---

## References & Tools
- React Native Upgrade Helper: upgrade-helper.vercel.app
- Android Compose Migration: developer.android.com/jetpack/compose
- Swift Concurrency: swift.org/concurrency
- Capacitor Documentation: capacitorjs.com/docs
- Flutter Version Channels: flutter.dev/docs/release/archive
