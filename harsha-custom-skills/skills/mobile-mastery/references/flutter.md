# Flutter Comprehensive Reference Guide

> **NOTE (March 2026):** This file is maintained for backward compatibility as part of the broader **mobile-app-mastery** skill.
>
> For **comprehensive, actively-maintained Flutter development**, use the dedicated **flutter-master** skill which covers:
> - Flutter 3.38+ / Dart 3.10+ with 89+ specialized reference files
> - Deep coverage: debugging, UI/UX, Android, iOS, production deployment, animations, performance optimization, testing, CI/CD
> - Platform-specific mastery (Apple HIG, Material You, Impeller, Xcode integration)
> - Advanced features: state management (Riverpod 3.0, BLoC 9.0+), custom painters, shader effects, isolates
>
> **Use flutter-master when:**
> - Building production-grade Flutter apps requiring deep optimization
> - Working on complex features (animations, native integration, performance tuning)
> - Needing platform-specific guidance (iOS/Android platform mastery)
> - Reviewing Flutter architecture and testing strategies
>
> **Use this file when:**
> - You need a quick generalist overview of Flutter fundamentals
> - Comparing Flutter with other cross-platform frameworks (React Native, KMP, etc.)
> - Working within the mobile-app-mastery ecosystem for multi-framework projects

---

Production-ready reference for building scalable, performant Flutter applications.

## Table of Contents

- [1. Dart Essentials](#1-dart-essentials)
- [2. Architecture: Widget/Element/Render Trees](#2-architecture-widgetelement-render-trees)
- [3. Project Structure: Feature-Based Clean Architecture](#3-project-structure-feature-based-clean-architecture)
- [4. Widget Lifecycle](#4-widget-lifecycle)
- [5. Navigation: GoRouter & Navigator 2.0](#5-navigation-gorouter--navigator-20)
- [6. State Management](#6-state-management)
- [7. Theming: Material Design 3](#7-theming-material-design-3)
- [8. Platform Channels: Native Integration](#8-platform-channels-native-integration)
- [9. Performance Optimization](#9-performance-optimization)
- [10. Testing: Comprehensive Coverage](#10-testing-comprehensive-coverage)
- [11. Animations](#11-animations)
- [12. Push Notifications](#12-push-notifications)
- [13. CI/CD: Automated Builds & Deployment](#13-cicd-automated-builds--deployment)
- [14. Common Pitfalls & Solutions](#14-common-pitfalls--solutions)

---

## 1. Dart Essentials

### Null Safety

Dart's null safety (introduced in Dart 2.12) eliminates null reference errors at compile time.

```dart
// Non-nullable by default
String name = "John"; // Cannot be null
String? nullableName; // Can be null

// Null coalescing operator
String username = nullableName ?? "Guest";

// Null assertion operator (use cautiously)
String nonNullName = nullableName!;

// Late initialization
late String lazyString;
lazyString = "Initialized later";

// Pattern matching with null checks (Dart 3.0+)
if (data case [var first, var second]) {
  print('First: $first, Second: $second');
}
```

### Async/Await Pattern

Manage asynchronous operations cleanly.

```dart
// Basic async/await
Future<String> fetchUserData() async {
  try {
    final response = await http.get(Uri.parse('https://api.example.com/user'));
    if (response.statusCode == 200) {
      return response.body;
    } else {
      throw Exception('Failed to load user');
    }
  } catch (e) {
    print('Error: $e');
    rethrow;
  }
}

// Multiple concurrent operations
Future<void> loadAppData() async {
  final results = await Future.wait([
    fetchUserData(),
    fetchSettings(),
    fetchNotifications(),
  ]);
  // Handle results
}

// Timeout handling
try {
  final data = await fetchUserData().timeout(
    const Duration(seconds: 5),
    onTimeout: () => throw Exception('Request timeout'),
  );
} catch (e) {
  print('Error: $e');
}
```

### Streams

Handle asynchronous sequences of events.

```dart
// Creating a stream
Stream<int> countStream() async* {
  for (int i = 0; i < 10; i++) {
    await Future.delayed(Duration(seconds: 1));
    yield i;
  }
}

// Listening to streams
void subscribeToStream() {
  countStream().listen(
    (value) => print('Value: $value'),
    onError: (error) => print('Error: $error'),
    onDone: () => print('Stream completed'),
  );
}

// Stream transformations
countStream()
    .where((value) => value.isEven)
    .map((value) => value * 2)
    .listen((value) => print('Transformed: $value'));

// Stream controllers
StreamController<String> controller = StreamController<String>();
controller.add('Event 1');
controller.add('Event 2');
controller.close();
```

### Sealed Classes (Dart 3.0+)

Enable exhaustive pattern matching for type-safe union types.

```dart
sealed class Result<T> {
  const Result();
}

class Success<T> extends Result<T> {
  final T data;
  const Success(this.data);
}

class Error<T> extends Result<T> {
  final Exception exception;
  const Error(this.exception);
}

class Loading<T> extends Result<T> {
  const Loading();
}

// Pattern matching (exhaustive, compiler-checked)
String handleResult<T>(Result<T> result) => switch (result) {
  Success(data: var data) => 'Success: $data',
  Error(exception: var e) => 'Error: $e',
  Loading() => 'Loading...',
};
```

### Extensions

Add methods to existing classes without inheritance.

```dart
extension StringExtensions on String {
  bool get isValidEmail => contains('@') && contains('.');

  String capitalize() => '${this[0].toUpperCase()}${substring(1)}';

  String toTitleCase() => split(' ')
      .map((word) => word.capitalize())
      .join(' ');
}

extension IntExtensions on int {
  Duration get milliseconds => Duration(milliseconds: this);
  Duration get seconds => Duration(seconds: this);

  bool get isEven => this % 2 == 0;
  bool get isOdd => this % 2 != 0;
}

// Usage
print("hello world".toTitleCase()); // Hello World
print(5.seconds); // 0:00:05.000000
```

---

## 2. Architecture: Widget/Element/Render Trees

Understanding Flutter's three-layer tree structure is crucial for performance optimization.

```dart
// The Widget Tree (immutable declarations)
// └─ StatelessWidget / StatefulWidget / InheritedWidget
//    └─ build() → Returns widget tree

// The Element Tree (stateful instances)
// └─ StatelessElement / StatefulElement
//    └─ Manages widget lifecycle & rebuild logic

// The Render Tree (layout & painting)
// └─ RenderObject subclasses
//    └─ performLayout(), paint()

// Example showing the three layers:
class MyWidget extends StatefulWidget {
  @override
  State<MyWidget> createState() => _MyWidgetState();
}

class _MyWidgetState extends State<MyWidget> {
  int count = 0;

  @override
  Widget build(BuildContext context) {
    // Widget tree: declarative UI
    return Center(
      child: Column(
        children: [
          Text('Count: $count'),
          ElevatedButton(
            onPressed: () => setState(() => count++),
            child: const Text('Increment'),
          ),
        ],
      ),
    );
  }
}

// Rendering pipeline:
// 1. Widget declared → Element created/updated
// 2. Element rebuild triggered
// 3. RenderObject layout calculated
// 4. Paint commands generated
// 5. Composited frame rasterized
```

---

## 3. Project Structure: Feature-Based Clean Architecture

```
lib/
├── main.dart
├── config/
│   ├── theme/
│   │   ├── app_theme.dart
│   │   └── colors.dart
│   ├── routes/
│   │   ├── app_routes.dart
│   │   └── route_guards.dart
│   └── constants/
│       └── app_constants.dart
├── core/
│   ├── errors/
│   │   ├── exceptions.dart
│   │   └── failures.dart
│   ├── network/
│   │   ├── api_client.dart
│   │   └── network_info.dart
│   ├── usecases/
│   │   └── usecase.dart
│   └── utils/
│       ├── logger.dart
│       └── validators.dart
├── features/
│   ├── authentication/
│   │   ├── data/
│   │   │   ├── datasources/
│   │   │   ├── models/
│   │   │   └── repositories/
│   │   ├── domain/
│   │   │   ├── entities/
│   │   │   ├── repositories/
│   │   │   └── usecases/
│   │   └── presentation/
│   │       ├── bloc/
│   │       ├── pages/
│   │       └── widgets/
│   ├── home/
│   │   ├── data/
│   │   ├── domain/
│   │   └── presentation/
│   └── profile/
│       ├── data/
│       ├── domain/
│       └── presentation/
└── injection_container.dart
```

**Rationale**: Feature-based architecture improves scalability, team collaboration, and code reusability while maintaining clear separation of concerns.

---

## 4. Widget Lifecycle

### StatelessWidget

Immutable widgets with no internal state.

```dart
class StatelessExample extends StatelessWidget {
  final String title;

  const StatelessExample({Key? key, required this.title}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    // Called whenever parent rebuilds
    // No setState available
    return Text(title);
  }
}
```

### StatefulWidget

Mutable widgets that manage internal state.

```dart
class StatefulExample extends StatefulWidget {
  final String initialValue;

  const StatefulExample({Key? key, required this.initialValue}) : super(key: key);

  @override
  State<StatefulExample> createState() => _StatefulExampleState();
}

class _StatefulExampleState extends State<StatefulExample>
    with WidgetsBindingObserver {
  late String value;

  @override
  void initState() {
    super.initState();
    // Initialization logic, subscriptions, API calls
    value = widget.initialValue;
    WidgetsBinding.instance.addObserver(this);
  }

  @override
  void didUpdateWidget(StatefulExample oldWidget) {
    super.didUpdateWidget(oldWidget);
    // Called when parent rebuilds with different properties
    if (oldWidget.initialValue != widget.initialValue) {
      value = widget.initialValue;
    }
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    switch (state) {
      case AppLifecycleState.resumed:
        print('App resumed');
        break;
      case AppLifecycleState.paused:
        print('App paused');
        break;
      case AppLifecycleState.detached:
        print('App detached');
        break;
      case AppLifecycleState.inactive:
        print('App inactive');
        break;
      case AppLifecycleState.hidden:
        print('App hidden');
        break;
    }
  }

  @override
  void deactivate() {
    // Called when widget removed from tree
    super.deactivate();
  }

  @override
  void dispose() {
    // Clean up: cancel subscriptions, dispose controllers
    WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Text(value);
  }
}
```

### InheritedWidget

Efficiently pass data down the widget tree.

```dart
class ThemeInheritedWidget extends InheritedWidget {
  final ThemeData themeData;
  final void Function(ThemeData) updateTheme;

  const ThemeInheritedWidget({
    Key? key,
    required this.themeData,
    required this.updateTheme,
    required Widget child,
  }) : super(key: key, child: child);

  static ThemeInheritedWidget of(BuildContext context) {
    return context.dependOnInheritedWidgetOfExactType<ThemeInheritedWidget>()!;
  }

  @override
  bool updateShouldNotify(ThemeInheritedWidget oldWidget) {
    return oldWidget.themeData != themeData;
  }
}

// Usage
final theme = ThemeInheritedWidget.of(context);
```

---

## 5. Navigation: GoRouter & Navigator 2.0

### GoRouter (Recommended)

Modern declarative routing with deep linking support.

```dart
// Define routes
final GoRouter router = GoRouter(
  initialLocation: '/',
  routes: [
    GoRoute(
      path: '/',
      builder: (context, state) => const HomePage(),
      routes: [
        GoRoute(
          path: 'profile/:userId',
          builder: (context, state) {
            final userId = state.pathParameters['userId']!;
            return ProfilePage(userId: userId);
          },
          redirect: (context, state) {
            // Route guards
            final isAuthenticated = context.read<AuthCubit>().state.isAuthenticated;
            if (!isAuthenticated) {
              return '/login';
            }
            return null;
          },
        ),
        GoRoute(
          path: 'settings',
          builder: (context, state) => const SettingsPage(),
        ),
      ],
    ),
    GoRoute(
      path: '/login',
      builder: (context, state) => const LoginPage(),
    ),
  ],
  errorBuilder: (context, state) => const ErrorPage(),
);

// In MaterialApp
MaterialApp.router(
  routerConfig: router,
  theme: ThemeData.light(),
  darkTheme: ThemeData.dark(),
  themeMode: ThemeMode.system,
)

// Navigate programmatically
context.go('/profile/123');
context.push('/settings');
context.pop();

// Get current route state
final state = GoRouterState.of(context);
print(state.uri); // Full URI
print(state.matchedLocation); // Route path
```

### Navigator 2.0

Manual route management for complex scenarios.

```dart
class NavigatorApp extends StatefulWidget {
  @override
  State<NavigatorApp> createState() => _NavigatorAppState();
}

class _NavigatorAppState extends State<NavigatorApp> {
  final GlobalKey<NavigatorState> navigatorKey = GlobalKey();
  final RouteDelegate delegate = RouteDelegate();

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Navigator(
        key: navigatorKey,
        pages: delegate.pages,
        onPopPage: (route, result) {
          if (!route.didPop(result)) return false;
          delegate.pop();
          return true;
        },
      ),
    );
  }
}
```

---

## 6. State Management

### Provider (Recommended for simplicity)

```dart
// Define a ChangeNotifier
class CounterProvider extends ChangeNotifier {
  int _count = 0;

  int get count => _count;

  void increment() {
    _count++;
    notifyListeners();
  }

  void decrement() {
    _count--;
    notifyListeners();
  }
}

// Setup providers
final counterProvider = ChangeNotifierProvider((ref) => CounterProvider());

// Usage in widgets
class CounterWidget extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final counter = ref.watch(counterProvider);

    return Column(
      children: [
        Text('Count: ${counter.count}'),
        ElevatedButton(
          onPressed: () => counter.increment(),
          child: const Text('Increment'),
        ),
      ],
    );
  }
}
```

### Riverpod (Type-safe Provider)

```dart
// Define state providers
final counterProvider = StateProvider<int>((ref) => 0);

final doubleCountProvider = Provider<int>((ref) {
  final count = ref.watch(counterProvider);
  return count * 2;
});

// Async operations
final userProvider = FutureProvider<User>((ref) async {
  final response = await http.get(Uri.parse('https://api.example.com/user'));
  return User.fromJson(jsonDecode(response.body));
});

// Usage with Riverpod
class MyWidget extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final count = ref.watch(counterProvider);
    final doubleCount = ref.watch(doubleCountProvider);
    final userAsync = ref.watch(userProvider);

    return Column(
      children: [
        Text('Count: $count, Double: $doubleCount'),
        userAsync.when(
          data: (user) => Text('User: ${user.name}'),
          loading: () => const CircularProgressIndicator(),
          error: (error, stack) => Text('Error: $error'),
        ),
        ElevatedButton(
          onPressed: () => ref.read(counterProvider.notifier).state++,
          child: const Text('Increment'),
        ),
      ],
    );
  }
}
```

### Bloc/Cubit (Event-driven)

```dart
// Define events
abstract class CounterEvent {}
class IncrementEvent extends CounterEvent {}
class DecrementEvent extends CounterEvent {}

// Define states
abstract class CounterState {}
class CounterInitial extends CounterState {}
class CounterUpdated extends CounterState {
  final int count;
  CounterUpdated(this.count);
}

// Implement Bloc
class CounterBloc extends Bloc<CounterEvent, CounterState> {
  int _count = 0;

  CounterBloc() : super(CounterInitial()) {
    on<IncrementEvent>((event, emit) {
      _count++;
      emit(CounterUpdated(_count));
    });

    on<DecrementEvent>((event, emit) {
      _count--;
      emit(CounterUpdated(_count));
    });
  }
}

// Usage
context.read<CounterBloc>().add(IncrementEvent());

BlocBuilder<CounterBloc, CounterState>(
  builder: (context, state) {
    if (state is CounterUpdated) {
      return Text('Count: ${state.count}');
    }
    return const SizedBox.shrink();
  },
)
```

### GetX (All-in-one solution)

```dart
class CounterController extends GetxController {
  final count = 0.obs;

  void increment() => count.value++;
  void decrement() => count.value--;
}

// Usage
GetBuilder<CounterController>(
  builder: (controller) => Text('Count: ${controller.count.value}'),
)

// Or with Obx
Obx(() => Text('Count: ${Get.find<CounterController>().count.value}'))
```

---

## 7. Theming: Material Design 3

### Dynamic Theming with Dark Mode

```dart
class ThemeProvider extends ChangeNotifier {
  ThemeMode _themeMode = ThemeMode.system;
  Color _seedColor = Colors.blue;

  ThemeMode get themeMode => _themeMode;
  Color get seedColor => _seedColor;

  void toggleTheme() {
    _themeMode = _themeMode == ThemeMode.light
        ? ThemeMode.dark
        : ThemeMode.light;
    notifyListeners();
  }

  void setSeedColor(Color color) {
    _seedColor = color;
    notifyListeners();
  }
}

// Material Design 3 theme
class AppTheme {
  static ThemeData lightTheme(Color seedColor) {
    return ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: seedColor,
        brightness: Brightness.light,
      ),
      appBarTheme: AppBarTheme(
        backgroundColor: seedColor,
        foregroundColor: Colors.white,
        elevation: 0,
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: seedColor,
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
        ),
      ),
    );
  }

  static ThemeData darkTheme(Color seedColor) {
    return ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: seedColor,
        brightness: Brightness.dark,
      ),
      scaffoldBackgroundColor: Colors.grey[900],
    );
  }
}

// Apply in main.dart
Consumer<ThemeProvider>(
  builder: (context, themeProvider, _) {
    return MaterialApp(
      theme: AppTheme.lightTheme(themeProvider.seedColor),
      darkTheme: AppTheme.darkTheme(themeProvider.seedColor),
      themeMode: themeProvider.themeMode,
      home: const HomePage(),
    );
  },
)
```

---

## 8. Platform Channels: Native Integration

### MethodChannel (Dart → Native)

```dart
// Dart side
class NativeService {
  static const platform = MethodChannel('com.example.app/native');

  static Future<String> getBatteryLevel() async {
    try {
      final result = await platform.invokeMethod<String>('getBatteryLevel');
      return result ?? 'Unknown';
    } catch (e) {
      return 'Error: $e';
    }
  }

  static Future<void> startLocationTracking() async {
    try {
      await platform.invokeMethod('startLocationTracking');
    } catch (e) {
      print('Error: $e');
    }
  }
}

// Swift side (iOS)
import Flutter

@main
@objc class GeneratedPluginRegistrant: NSObject {
  static func register(with registry: FlutterPluginRegistry) {
    // Registration code
  }
}

class FlutterViewController: UIViewController, FlutterPlatformView {
  override func viewDidLoad() {
    super.viewDidLoad()

    let controller = window?.rootViewController as! FlutterViewController
    let batteryChannel = FlutterMethodChannel(
      name: "com.example.app/native",
      binaryMessenger: controller.binaryMessenger
    )

    batteryChannel.setMethodCallHandler { (call: FlutterMethodCall, result: @escaping FlutterResult) -> Void in
      switch call.method {
      case "getBatteryLevel":
        let batteryLevel = UIDevice.current.batteryLevel
        result(String(Int(batteryLevel * 100)))
      case "startLocationTracking":
        self.startLocationTracking()
        result(nil)
      default:
        result(FlutterMethodNotImplemented)
      }
    }
  }

  private func startLocationTracking() {
    // Implementation
  }
}

// Kotlin side (Android)
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.embedding.engine.dart.DartExecutor
import io.flutter.plugin.common.MethodChannel

class MainActivity: FlutterActivity() {
  private val CHANNEL = "com.example.app/native"

  override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
    super.configureFlutterEngine(flutterEngine)

    MethodChannel(flutterEngine.dartExecutor.binaryMessenger, CHANNEL)
      .setMethodCallHandler { call, result ->
        when (call.method) {
          "getBatteryLevel" -> {
            val batteryLevel = getBatteryLevel()
            result(batteryLevel)
          }
          "startLocationTracking" -> {
            startLocationTracking()
            result(null)
          }
          else -> result(null)
        }
      }
  }

  private fun getBatteryLevel(): String {
    val batteryManager = getSystemService(Context.BATTERY_SERVICE) as BatteryManager
    return batteryManager.getIntProperty(BatteryManager.BATTERY_PROPERTY_CHARGE_COUNTER).toString()
  }

  private fun startLocationTracking() {
    // Implementation
  }
}
```

### EventChannel (Native → Dart)

```dart
// Dart side
class LocationService {
  static const eventChannel = EventChannel('com.example.app/location');

  static Stream<double> get locationUpdates {
    return eventChannel.receiveBroadcastStream().map((event) {
      return event as double;
    });
  }
}

// Usage
LocationService.locationUpdates.listen((latitude) {
  print('New latitude: $latitude');
});

// Swift side
let locationChannel = FlutterEventChannel(
  name: "com.example.app/location",
  binaryMessenger: controller.binaryMessenger
)

locationChannel.setStreamHandler(LocationStreamHandler())

class LocationStreamHandler: NSObject, FlutterStreamHandler {
  var eventSink: FlutterEventSink?

  func onListen(withArguments arguments: Any?, eventSink: @escaping FlutterEventSink) -> FlutterError? {
    self.eventSink = eventSink
    startLocationUpdates()
    return nil
  }

  func onCancel(withArguments arguments: Any?) -> FlutterError? {
    stopLocationUpdates()
    return nil
  }

  private func startLocationUpdates() {
    // Emit location updates
    eventSink?(37.7749)
  }
}
```

---

## 9. Performance Optimization

### Impeller Rendering Engine

Enable Impeller for improved graphics rendering:

```dart
// Enable in pubspec.yaml
flutter:
  enable-impeller: true

// Or via command line
flutter run --enable-impeller
```

### RepaintBoundary & ConstConstructors

```dart
class PerformanceOptimizedWidget extends StatelessWidget {
  const PerformanceOptimizedWidget({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // Prevent unnecessary rebuilds
        RepaintBoundary(
          child: ExpensiveWidget(),
        ),
        // Use const constructors
        const SizedBox(height: 16),
        const Text('Static Text'),
      ],
    );
  }
}

// Expensive widget with const constructor
class ExpensiveWidget extends StatelessWidget {
  final String data;

  const ExpensiveWidget({Key? key, required this.data}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.blue,
      child: Text(data),
    );
  }
}
```

### Lazy Loading & ListView.builder

```dart
ListView.builder(
  itemCount: items.length,
  itemBuilder: (context, index) {
    return ListTile(
      title: Text(items[index].title),
      trailing: CachedNetworkImage(
        imageUrl: items[index].imageUrl,
        placeholder: (context, url) => const CircularProgressIndicator(),
        errorWidget: (context, url, error) => const Icon(Icons.error),
      ),
    );
  },
)

// For grids
GridView.builder(
  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
    crossAxisCount: 2,
    childAspectRatio: 1.0,
  ),
  itemCount: items.length,
  itemBuilder: (context, index) => ProductCard(items[index]),
)
```

---

## 10. Testing: Comprehensive Coverage

### Unit Tests

```dart
import 'package:test/test.dart';

void main() {
  group('CounterService', () {
    late CounterService counterService;

    setUp(() {
      counterService = CounterService();
    });

    test('should increment counter', () {
      counterService.increment();
      expect(counterService.count, 1);
    });

    test('should decrement counter', () {
      counterService.increment();
      counterService.decrement();
      expect(counterService.count, 0);
    });
  });
}
```

### Widget Tests

```dart
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('CounterWidget', () {
    testWidgets('displays initial count', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(body: CounterWidget()),
        ),
      );

      expect(find.text('Count: 0'), findsOneWidget);
    });

    testWidgets('increments count on button tap', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(body: CounterWidget()),
        ),
      );

      await tester.tap(find.byIcon(Icons.add));
      await tester.pump();

      expect(find.text('Count: 1'), findsOneWidget);
    });
  });
}
```

### Golden Tests

```dart
testWidgets('Golden test for CounterWidget', (WidgetTester tester) async {
  await tester.binding.window.physicalSizeTestValue = const Size(400, 800);
  addTearDown(tester.binding.window.clearPhysicalSizeTestValue);

  await tester.pumpWidget(
    MaterialApp(
      home: Scaffold(body: CounterWidget()),
    ),
  );

  await expectLater(
    find.byType(CounterWidget),
    matchesGoldenFile('counter_widget.png'),
  );
});
```

### Integration Tests

```dart
import 'package:integration_test/integration_test.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('App Integration Tests', () {
    testWidgets('Full user flow', (WidgetTester tester) async {
      await tester.pumpWidget(const MyApp());

      expect(find.text('Welcome'), findsOneWidget);
      await tester.tap(find.byType(ElevatedButton));
      await tester.pumpAndSettle();

      expect(find.text('Home'), findsOneWidget);
    });
  });
}
```

---

## 11. Animations

### Implicit Animations

```dart
class ImplicitAnimationExample extends StatefulWidget {
  @override
  State<ImplicitAnimationExample> createState() =>
      _ImplicitAnimationExampleState();
}

class _ImplicitAnimationExampleState extends State<ImplicitAnimationExample> {
  bool expanded = false;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        AnimatedContainer(
          duration: const Duration(milliseconds: 500),
          width: expanded ? 200 : 100,
          height: expanded ? 200 : 100,
          color: expanded ? Colors.blue : Colors.red,
          child: GestureDetector(
            onTap: () => setState(() => expanded = !expanded),
            child: const Center(child: Text('Tap me')),
          ),
        ),
        const SizedBox(height: 20),
        AnimatedOpacity(
          opacity: expanded ? 1.0 : 0.0,
          duration: const Duration(seconds: 1),
          child: const Text('Fade effect'),
        ),
      ],
    );
  }
}
```

### Explicit Animations

```dart
class ExplicitAnimationExample extends StatefulWidget {
  @override
  State<ExplicitAnimationExample> createState() =>
      _ExplicitAnimationExampleState();
}

class _ExplicitAnimationExampleState extends State<ExplicitAnimationExample>
    with TickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _opacity;
  late Animation<Offset> _offset;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    );

    _opacity = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeIn),
    );

    _offset = Tween<Offset>(begin: const Offset(-1, 0), end: Offset.zero)
        .animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeOut),
    );

    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return SlideTransition(
      position: _offset,
      child: FadeTransition(
        opacity: _opacity,
        child: const Text('Animated widget'),
      ),
    );
  }
}
```

### Hero Animation

```dart
class HeroAnimationExample extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => Navigator.push(context, MaterialPageRoute(
        builder: (context) => const DetailPage(),
      )),
      child: Hero(
        tag: 'product-image',
        child: Image.asset('assets/product.png', width: 100),
      ),
    );
  }
}

class DetailPage extends StatelessWidget {
  const DetailPage();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Details')),
      body: Center(
        child: Hero(
          tag: 'product-image',
          child: Image.asset('assets/product.png'),
        ),
      ),
    );
  }
}
```

### Rive Animations

```dart
// pubspec.yaml
dependencies:
  rive: ^0.13.0

// Implementation
class RiveAnimationExample extends StatefulWidget {
  @override
  State<RiveAnimationExample> createState() => _RiveAnimationExampleState();
}

class _RiveAnimationExampleState extends State<RiveAnimationExample> {
  late RiveAnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = OneShotAnimation('bounce', autoplay: true);
  }

  @override
  Widget build(BuildContext context) {
    return RiveAnimation.asset(
      'assets/animations/animation.riv',
      controllers: [_controller],
      onInit: (_) {},
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }
}
```

---

## 12. Push Notifications

### Firebase Cloud Messaging (FCM)

```dart
// Setup
import 'package:firebase_messaging/firebase_messaging.dart';

class NotificationService {
  final FirebaseMessaging _firebaseMessaging = FirebaseMessaging.instance;

  Future<void> initialize() async {
    // Request permissions (iOS)
    await _firebaseMessaging.requestPermission(
      alert: true,
      announcement: false,
      badge: true,
      carPlay: false,
      criticalAlert: false,
      provisional: false,
      sound: true,
    );

    // Get token
    final token = await _firebaseMessaging.getToken();
    print('FCM Token: $token');

    // Handle foreground messages
    FirebaseMessaging.onMessage.listen((RemoteMessage message) {
      print('Message: ${message.notification?.title}');
      if (message.notification != null) {
        showLocalNotification(
          message.notification!.title ?? 'Title',
          message.notification!.body ?? 'Body',
        );
      }
    });

    // Handle background messages
    FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);
  }

  void showLocalNotification(String title, String body) {
    // Use flutter_local_notifications
  }
}

Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  print('Background message: ${message.notification?.title}');
}
```

### Local Notifications

```dart
import 'package:flutter_local_notifications/flutter_local_notifications.dart';

class LocalNotificationService {
  static final FlutterLocalNotificationsPlugin _notificationsPlugin =
      FlutterLocalNotificationsPlugin();

  static Future<void> initialize() async {
    const AndroidInitializationSettings androidInitSettings =
        AndroidInitializationSettings('@mipmap/ic_launcher');

    const DarwinInitializationSettings iosInitSettings =
        DarwinInitializationSettings(
      requestAlertPermission: true,
      requestBadgePermission: true,
      requestSoundPermission: true,
    );

    const InitializationSettings initSettings = InitializationSettings(
      android: androidInitSettings,
      iOS: iosInitSettings,
    );

    await _notificationsPlugin.initialize(
      initSettings,
      onDidReceiveNotificationResponse: (NotificationResponse response) {
        print('Notification tapped: ${response.payload}');
      },
    );
  }

  static Future<void> showNotification({
    required int id,
    required String title,
    required String body,
    String? payload,
  }) async {
    const AndroidNotificationDetails androidDetails =
        AndroidNotificationDetails(
      'channel_id',
      'Default Channel',
      channelDescription: 'Default notification channel',
      importance: Importance.max,
      priority: Priority.high,
    );

    const DarwinNotificationDetails iosDetails = DarwinNotificationDetails();

    const NotificationDetails details = NotificationDetails(
      android: androidDetails,
      iOS: iosDetails,
    );

    await _notificationsPlugin.show(id, title, body, details, payload: payload);
  }

  static Future<void> cancelNotification(int id) async {
    await _notificationsPlugin.cancel(id);
  }
}
```

---

## 13. CI/CD: Automated Builds & Deployment

### Codemagic Configuration

```yaml
# codemagic.yaml
workflows:
  ios-release:
    name: iOS Release
    environment:
      xcode: latest
      flutter: stable
    scripts:
      - flutter pub get
      - flutter test
      - flutter build ios --release
    artifacts:
      - build/ios/ipa/*.ipa

  android-release:
    name: Android Release
    environment:
      android-ndk: r21e
      flutter: stable
    scripts:
      - flutter pub get
      - flutter test
      - flutter build appbundle --release
    artifacts:
      - build/app/outputs/bundle/release/*.aab

  deploy:
    name: Deploy to Firebase
    environment:
      flutter: stable
    dependencies:
      - ios-release
      - android-release
    scripts:
      - firebase deploy --token "$FIREBASE_TOKEN"
```

### Fastlane Integration

```ruby
# fastlane/Fastfile
default_platform(:ios)

platform :ios do
  desc "Build and upload to TestFlight"
  lane :beta do
    setup_ci
    match(type: "appstore")
    build_app(
      workspace: "ios/Runner.xcworkspace",
      scheme: "Runner",
      configuration: "Release",
      export_method: "app-store",
      destination: "generic/platform=iOS"
    )
    upload_to_testflight(
      username: ENV["APPLE_ID"],
      app_identifier: "com.example.app"
    )
  end
end

platform :android do
  desc "Build and upload to Google Play"
  lane :beta do
    gradle(
      project_dir: "android/",
      task: "bundleRelease"
    )
    upload_to_play_store(
      track: "beta",
      json_key: ENV["ANDROID_JSON_KEY_FILE"],
      aab: "android/app/build/outputs/bundle/release/app-release.aab"
    )
  end
end
```

### Flavors for Multiple Environments

```yaml
# pubspec.yaml
flutter:
  flavors:
    development:
      apiUrl: https://dev-api.example.com
      appName: MyApp Dev
    staging:
      apiUrl: https://staging-api.example.com
      appName: MyApp Staging
    production:
      apiUrl: https://api.example.com
      appName: MyApp
```

```dart
// main.dart with environment
void main() async {
  const flavor = String.fromEnvironment('FLAVOR', defaultValue: 'development');
  Config.initialize(flavor: flavor);
  runApp(const MyApp());
}

// Build commands
// flutter run -t lib/main_dev.dart
// flutter build apk --dart-define=FLAVOR=production
```

---

## 14. Common Pitfalls & Solutions

### 1. Rebuilds Too Frequently

**Problem**: Entire widget tree rebuilds on state change.

**Solution**:
```dart
// Use const constructors
const SizedBox(height: 16);

// Use RepaintBoundary
RepaintBoundary(child: ExpensiveWidget());

// Use shouldRebuild in InheritedWidget
bool updateShouldNotify(OldWidget old) => old.data != data;
```

### 2. Memory Leaks

**Problem**: Subscriptions/controllers not disposed.

**Solution**:
```dart
@override
void dispose() {
  _streamSubscription?.cancel();
  _controller?.dispose();
  _animationController?.dispose();
  super.dispose();
}
```

### 3. Blocking UI Thread

**Problem**: Long operations freeze UI.

**Solution**:
```dart
// Use isolates
final result = await compute(heavyComputation, data);

// Or use FutureBuilder
FutureBuilder<Data>(
  future: fetchData(),
  builder: (context, snapshot) {
    if (snapshot.connectionState == ConnectionState.waiting) {
      return const CircularProgressIndicator();
    }
    return Text('Data: ${snapshot.data}');
  },
)
```

### 4. Not Handling Async Errors

**Problem**: Unhandled async exceptions crash app.

**Solution**:
```dart
try {
  final data = await fetchData();
} on SocketException catch (e) {
  print('Network error: $e');
} on FormatException catch (e) {
  print('Format error: $e');
} catch (e) {
  print('Unknown error: $e');
}
```

### 5. Incorrect Navigator Usage

**Problem**: Navigator.pop() from wrong context.

**Solution**:
```dart
// Use global navigation key
final navigatorKey = GlobalKey<NavigatorState>();

// In MaterialApp
MaterialApp(navigatorKey: navigatorKey, ...)

// Navigate safely
navigatorKey.currentState?.pop();
```

### 6. Missing Keys in Lists

**Problem**: List items get reordered incorrectly.

**Solution**:
```dart
// Always use unique keys for list items
ListView.builder(
  itemBuilder: (context, index) {
    return ListTile(
      key: ValueKey(items[index].id), // Unique key
      title: Text(items[index].title),
    );
  },
)
```

### 7. Expensive Widgets in build()

**Problem**: Creating objects in build() causes performance issues.

**Solution**:
```dart
class MyWidget extends StatefulWidget {
  @override
  State<MyWidget> createState() => _MyWidgetState();
}

class _MyWidgetState extends State<MyWidget> {
  late final _expensiveObject = ExpensiveClass();

  @override
  void initState() {
    super.initState();
    _expensiveObject = ExpensiveClass(); // Create once in initState
  }

  @override
  Widget build(BuildContext context) {
    return Text(_expensiveObject.value); // Use pre-created object
  }
}
```

### 8. Not Handling App Lifecycle

**Problem**: Resources leak when app pauses.

**Solution**:
```dart
class MyWidget extends StatefulWidget {
  @override
  State<MyWidget> createState() => _MyWidgetState();
}

class _MyWidgetState extends State<MyWidget> with WidgetsBindingObserver {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    switch (state) {
      case AppLifecycleState.resumed:
        _resumeOperations();
      case AppLifecycleState.paused:
        _pauseOperations();
      default:
        break;
    }
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }
}
```

### 9. Over-Nesting Widgets

**Problem**: Deep widget hierarchies reduce readability.

**Solution**:
```dart
// Extract widgets into separate classes
class _Header extends StatelessWidget {
  @override
  Widget build(BuildContext context) => AppBar(...);
}

class _Body extends StatelessWidget {
  @override
  Widget build(BuildContext context) => Column(...);
}

class MyPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: _Header(),
      body: _Body(),
    );
  }
}
```

### 10. Ignoring Platform Differences

**Problem**: UI breaks on different platforms.

**Solution**:
```dart
import 'dart:io';

class MyWidget extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Platform.isIOS
        ? CupertinoButton(onPressed: () {}, child: const Text('iOS'))
        : ElevatedButton(onPressed: () {}, child: const Text('Android'));
  }
}
```

---

## Summary

This reference covers production-ready patterns for building scalable Flutter applications. Focus on:

- **Null Safety & Type System**: Leverage Dart's powerful type system
- **Architecture**: Use clean architecture with feature-based structure
- **State Management**: Choose appropriate solution (Provider, Riverpod, Bloc)
- **Performance**: Optimize rendering, use lazy loading, const constructors
- **Testing**: Maintain high code coverage with unit, widget, and integration tests
- **Native Integration**: Use platform channels for iOS/Android features
- **Best Practices**: Follow official Flutter guidelines and community standards

Keep your code maintainable, testable, and performant by applying these patterns consistently across your projects.
