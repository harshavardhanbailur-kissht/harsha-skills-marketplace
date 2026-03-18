# Mobile Application Performance Reference Guide

Comprehensive guide to optimizing mobile application performance across iOS, Android, React Native, and Flutter with practical code examples and best practices.

## Table of Contents

- [1. Startup Optimization](#1-startup-optimization)
- [2. Memory Management](#2-memory-management)
- [3. CPU Optimization](#3-cpu-optimization)
- [4. Battery Optimization](#4-battery-optimization)
- [5. Network Optimization](#5-network-optimization)
- [6. Rendering Performance](#6-rendering-performance)
- [7. App Size Optimization](#7-app-size-optimization)
- [8. Lazy Loading Strategies](#8-lazy-loading-strategies)
- [9. Database Query Optimization](#9-database-query-optimization)
- [10. Image Loading Libraries](#10-image-loading-libraries)
- [11. Scroll Performance Optimization](#11-scroll-performance-optimization)
- [12. Profiling Tools](#12-profiling-tools)

## 1. Startup Optimization

### Cold/Warm/Hot Start Performance

**iOS - Cold Start Optimization**
```swift
// AppDelegate.swift
func application(_ application: UIApplication,
                 didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
    // Measure startup time
    let startTime = CACurrentMediaTime()

    // Defer non-critical initialization
    DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
        self.initializeAnalytics()
        self.setupRemoteNotifications()
    }

    let loadTime = CACurrentMediaTime() - startTime
    print("Startup time: \(loadTime)ms")

    return true
}

// Avoid expensive operations in +load methods
// Use lazy initialization for heavy resources
class DatabaseManager {
    static let shared = DatabaseManager()
    lazy var database: Database = {
        return Database(path: "app.db")
    }()
}
```

**Android - Cold Start Optimization**
```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Profile startup
        val startTime = System.currentTimeMillis()

        setContentView(R.layout.activity_main)

        // Defer initialization
        Handler(Looper.getMainLooper()).postDelayed({
            initializeThirdPartyLibraries()
        }, 500)

        val startupTime = System.currentTimeMillis() - startTime
        Log.d("Startup", "Time: ${startupTime}ms")
    }
}

// Application.kt - Lazy initialization
class MyApplication : Application() {
    val database: AppDatabase by lazy {
        Room.databaseBuilder(this, AppDatabase::class.java, "app.db").build()
    }

    val imageLoader: ImageLoader by lazy {
        ImageLoader.Builder(this).build()
    }
}
```

**React Native - Startup Optimization**
```javascript
// index.js - Measure startup
import { AppRegistry, LogBox } from 'react-native';
import App from './App';

const appName = 'MyApp';

const startTime = Date.now();

AppRegistry.registerComponent(appName, () => {
  return () => {
    React.useEffect(() => {
      const endTime = Date.now();
      console.log(`App startup: ${endTime - startTime}ms`);
    }, []);

    return <App />;
  };
});
```

**Flutter - Startup Optimization**
```dart
void main() {
  final stopwatch = Stopwatch()..start();

  WidgetsFlutterBinding.ensureInitialized();

  // Lazy initialize services
  initializeLazyServices();

  runApp(const MyApp());

  stopwatch.stop();
  print('Startup time: ${stopwatch.elapsedMilliseconds}ms');
}

Future<void> initializeLazyServices() async {
  // Defer non-critical initialization
  await Future.delayed(Duration(milliseconds: 100));
  // Initialize services
}
```

### Splash Screen Implementation
```kotlin
// Android splash screen strategy
class SplashActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val intent = Intent(this, MainActivity::class.java)
        startActivity(intent)
        finish()
    }
}
```

---

## 2. Memory Management

### Memory Leak Detection and Prevention

**iOS - ARC and WeakReference Patterns**
```swift
// Capture list to prevent retain cycles
class NetworkManager {
    var completionHandler: (() -> Void)?

    func fetchData(completion: @escaping () -> Void) {
        // Use [weak self] to avoid retain cycle
        URLSession.shared.dataTask(with: url) { [weak self] data, response, error in
            guard let self = self else { return }
            // self won't create a retain cycle
            completion()
        }.resume()
    }
}

// Proper delegation
class ViewController: UIViewController, UITableViewDelegate {
    let tableView = UITableView()

    override func viewDidLoad() {
        super.viewDidLoad()
        // Delegate won't create retain cycle (delegate is weak by default)
        tableView.delegate = self
    }
}
```

**Android - Garbage Collection and WeakReference**
```kotlin
// WeakReference for cache management
class ImageCache {
    private val cache = WeakHashMap<String, Bitmap>()

    fun get(key: String): Bitmap? = cache[key]

    fun put(key: String, bitmap: Bitmap) {
        cache[key] = bitmap
    }
}

// Fragment memory leak prevention
class MyFragment : Fragment() {
    private var listener: OnDataChangeListener? = null

    override fun onDestroyView() {
        super.onDestroyView()
        listener = null // Clear references
    }
}

// Proper listener cleanup
object EventBus {
    private val listeners = mutableListOf<WeakReference<EventListener>>()

    fun subscribe(listener: EventListener) {
        listeners.add(WeakReference(listener))
    }

    fun publish(event: Event) {
        listeners.forEach { ref ->
            ref.get()?.onEvent(event)
        }
        listeners.removeAll { it.get() == null }
    }
}
```

**React Native - Memory Profiling**
```javascript
// Profile memory usage
import { MemoryUtil } from 'react-native';

function trackMemory() {
  const memInfo = MemoryUtil.getMemoryInfo();
  console.log(`Used: ${memInfo.usedMemory}MB`);
  console.log(`Free: ${memInfo.freeMemory}MB`);
}

// Cleanup in useEffect
function MyComponent() {
  const [data, setData] = useState(null);

  useEffect(() => {
    let isMounted = true;

    fetchData().then(result => {
      if (isMounted) setData(result);
    });

    return () => {
      isMounted = false; // Prevent memory leaks
    };
  }, []);

  return <Text>{JSON.stringify(data)}</Text>;
}
```

**Flutter - Memory Management**
```dart
class MemoryManager {
  static void profileMemory() {
    DeviceInfoPlugin().androidInfo.then((info) {
      print('Device memory: ${info.totalMemory}');
    });
  }
}

// Proper resource cleanup
class StreamManager {
  late StreamSubscription subscription;

  void subscribe() {
    subscription = eventStream.listen((event) {
      // Handle event
    });
  }

  void dispose() {
    subscription.cancel(); // Always cancel subscriptions
  }
}
```

---

## 3. CPU Optimization

### Thread Management and Background Processing

**iOS - Thread Management**
```swift
// Use DispatchQueue for concurrent operations
class DataProcessor {
    private let processingQueue = DispatchQueue(label: "com.app.processing", attributes: .concurrent)

    func processLargeDataset(_ data: [Int]) {
        processingQueue.async { [weak self] in
            let result = data.map { $0 * 2 }
            DispatchQueue.main.async {
                self?.updateUI(with: result)
            }
        }
    }

    // Use QoS (Quality of Service)
    func performBackgroundTask() {
        DispatchQueue.global(qos: .background).async {
            // Heavy computation
        }
    }
}
```

**Android - Thread Management**
```kotlin
class DataProcessor {
    private val executorService = Executors.newFixedThreadPool(4)

    fun processData(data: List<Int>) {
        executorService.execute {
            val result = data.map { it * 2 }
            Handler(Looper.getMainLooper()).post {
                updateUI(result)
            }
        }
    }

    fun cleanup() {
        executorService.shutdown()
    }
}

// Using Coroutines (preferred)
class DataViewModel : ViewModel() {
    fun loadData() {
        viewModelScope.launch(Dispatchers.Default) {
            val data = heavyComputation()
            withContext(Dispatchers.Main) {
                updateUI(data)
            }
        }
    }
}
```

**React Native - CPU Optimization**
```javascript
// Use InteractionManager for heavy processing
import { InteractionManager } from 'react-native';

function processLargeDataset() {
  InteractionManager.runAfterInteractions(() => {
    // Heavy computation after user interaction completes
    const result = largeArray.map(item => complexCalculation(item));
  });
}

// Use FlatList with removeClippedSubviews
<FlatList
  data={items}
  renderItem={({ item }) => <ItemComponent item={item} />}
  removeClippedSubviews={true}
  maxToRenderPerBatch={10}
  updateCellsBatchingPeriod={50}
/>
```

**Flutter - Background Processing**
```dart
import 'package:workmanager/workmanager.dart';

void callbackDispatcher() {
  Workmanager().executeTask((task, inputData) {
    print('Background task executed: $task');
    return Future.value(true);
  });
}

void registerBackgroundTask() {
  Workmanager().initialize(callbackDispatcher);
  Workmanager().registerPeriodicTask(
    'unique_id',
    'simpleTask',
    frequency: Duration(hours: 1),
  );
}
```

---

## 4. Battery Optimization

### Energy Profiling and Power Management

**iOS - Battery Optimization**
```swift
import CoreLocation

class LocationManager: NSObject, CLLocationManagerDelegate {
    let locationManager = CLLocationManager()

    func optimizeForBattery() {
        // Use significant location changes instead of continuous updates
        locationManager.startMonitoringSignificantLocationChanges()

        // Or use lazy updates
        locationManager.pausesLocationUpdatesAutomatically = true
        locationManager.allowsBackgroundLocationUpdates = false
    }

    // Monitor low power mode
    func startMonitoringPowerState() {
        if ProcessInfo.processInfo.isLowPowerModeEnabled {
            // Reduce refresh rates, disable animations
            print("Low power mode enabled")
        }
    }
}

// Background task management
class BackgroundTaskManager {
    func scheduleBackgroundRefresh() {
        BGTaskScheduler.shared.submitTaskRequest(BGProcessingTaskRequest(identifier: "com.app.refresh"))
    }
}
```

**Android - Battery Optimization**
```kotlin
class BatteryManager(context: Context) {
    private val batteryManager = context.getSystemService(Context.BATTERY_SERVICE) as android.os.BatteryManager

    fun isBatteryLow(): Boolean {
        return batteryManager.lowBattery
    }

    fun optimizeForLowBattery() {
        val filter = IntentFilter(Intent.ACTION_BATTERY_CHANGED)
        val intent = context.registerReceiver(null, filter)
        val level = intent?.getIntExtra(BatteryManager.EXTRA_LEVEL, -1) ?: -1

        if (level < 20) {
            reduceRefreshRate()
            disableAnalytics()
        }
    }
}

// Work scheduling
class BackgroundSync {
    fun schedulePeriodicSync(context: Context) {
        val syncRequest = PeriodicWorkRequestBuilder<SyncWorker>(
            15, TimeUnit.MINUTES
        ).build()

        WorkManager.getInstance(context).enqueueUniquePeriodicWork(
            "sync", ExistingPeriodicWorkPolicy.KEEP, syncRequest
        )
    }
}
```

**React Native - Battery Optimization**
```javascript
import { AppState, Platform } from 'react-native';

class BatteryOptimizer {
  constructor() {
    this.appState = AppState.currentState;
    AppState.addEventListener('change', this.handleAppState);
  }

  handleAppState = (nextAppState) => {
    if (nextAppState === 'background') {
      this.pauseLocationUpdates();
      this.reduceRefreshRate();
    } else if (nextAppState === 'active') {
      this.resumeLocationUpdates();
    }
    this.appState = nextAppState;
  }
}
```

**Flutter - Battery and Background Scheduling**
```dart
import 'package:flutter_background_service/flutter_background_service.dart';

class BackgroundServiceManager {
  static Future<void> initializeBackgroundService() async {
    final service = FlutterBackgroundService();

    await service.configure(
      androidConfiguration: AndroidConfiguration(
        onStart: onStart,
        isForegroundMode: false,
      ),
    );
  }

  static void onStart(ServiceInstance service) {
    // Run background task
  }
}
```

---

## 5. Network Optimization

### Request Batching, Compression, and Image Optimization

**iOS - Network Optimization**
```swift
class NetworkBatcher {
    private var pendingRequests: [URLRequest] = []
    private var batchTimer: Timer?

    func queueRequest(_ request: URLRequest) {
        pendingRequests.append(request)

        if batchTimer == nil {
            batchTimer = Timer.scheduledTimer(withTimeInterval: 0.5, repeats: false) { _ in
                self.processBatch()
            }
        }
    }

    private func processBatch() {
        let session = URLSession(configuration: .default)

        for request in pendingRequests {
            var compressedRequest = request
            if let body = request.httpBody {
                compressedRequest.httpBody = try? (body as NSData).compressed(using: .lz4)
                compressedRequest.setValue("gzip", forHTTPHeaderField: "Content-Encoding")
            }

            session.dataTask(with: compressedRequest).resume()
        }

        pendingRequests.removeAll()
        batchTimer = nil
    }
}

// Image optimization
class ImageOptimizer {
    static func optimize(_ image: UIImage) -> UIImage? {
        let maxDimension: CGFloat = 800
        let scale = min(maxDimension / image.size.width, maxDimension / image.size.height)

        let newSize = CGSize(width: image.size.width * scale, height: image.size.height * scale)
        UIGraphicsBeginImageContextWithOptions(newSize, false, 0)
        image.draw(in: CGRect(origin: .zero, size: newSize))
        let scaledImage = UIGraphicsGetImageFromCurrentImageContext()
        UIGraphicsEndImageContext()

        return scaledImage
    }
}
```

**Android - Network Optimization**
```kotlin
class NetworkOptimizer {
    fun batchRequests(requests: List<ApiRequest>) {
        val batchRequest = BatchRequest()

        for (request in requests) {
            batchRequest.add(request)
        }

        // Send as single batch
        sendBatchRequest(batchRequest)
    }

    fun compressRequest(data: String): ByteArray {
        return data.toByteArray().let { original ->
            GZIPOutputStream(ByteArrayOutputStream()).use { gzip ->
                gzip.write(original)
                gzip.finish()
                gzip.javaClass.getDeclaredMethod("getBytes").invoke(gzip) as ByteArray
            }
        }
    }
}

// Image optimization with Coil
class ImageLoader {
    fun loadOptimized(context: Context, imageView: ImageView, url: String) {
        val loader = ImageLoader.Builder(context)
            .dispatcher(Dispatchers.IO)
            .memoryCache { MemoryCache.Builder(context).maxSizePercent(0.25).build() }
            .diskCache { DiskCache.Builder().directory(context.cacheDir).build() }
            .build()

        imageView.load(url, loader) {
            crossfade(true)
            transformations(RoundedCornersTransformation())
        }
    }
}
```

**React Native - Network Optimization**
```javascript
class RequestBatcher {
  constructor(batchDelay = 500) {
    this.queue = [];
    this.batchDelay = batchDelay;
    this.timer = null;
  }

  add(request) {
    this.queue.push(request);

    if (!this.timer) {
      this.timer = setTimeout(() => this.flush(), this.batchDelay);
    }
  }

  async flush() {
    if (this.queue.length === 0) return;

    const batch = this.queue.splice(0);
    const response = await fetch('/api/batch', {
      method: 'POST',
      body: JSON.stringify(batch),
      headers: { 'Content-Encoding': 'gzip' }
    });

    this.timer = null;
    return response.json();
  }
}

// Image optimization
function optimizeImage(uri) {
  return Image.resolveAssetSource(uri);
}
```

**Flutter - Network and Image Optimization**
```dart
class NetworkOptimizer {
  static Future<void> batchRequests(List<ApiRequest> requests) async {
    final batch = requests.map((r) => r.toJson()).toList();
    final response = await http.post(
      Uri.parse('https://api.example.com/batch'),
      headers: {'Content-Encoding': 'gzip'},
      body: jsonEncode(batch),
    );
  }
}

// Image loading with CachedNetworkImage
class ImageOptimizer {
  static Widget cachedImage(String url) {
    return CachedNetworkImage(
      imageUrl: url,
      memCacheHeight: 200,
      memCacheWidth: 200,
      cacheManager: CacheManager(
        Config(
          'cached_images',
          stalePeriod: Duration(days: 30),
          maxNrOfCacheObjects: 200,
        ),
      ),
    );
  }
}
```

---

## 6. Rendering Performance

### 60fps and GPU Profiling

**iOS - Rendering Optimization**
```swift
class RenderingOptimizer {
    // Enable Core Animation tool in Instruments
    static func optimizeLayerRendering(_ view: UIView) {
        // Rasterize expensive hierarchies
        view.layer.shouldRasterize = true
        view.layer.rasterizationScale = UIScreen.main.scale

        // Disable when view changes
        view.layer.shouldRasterize = false
    }

    // Reduce overdraw
    static func configureView(_ view: UIView) {
        view.layer.isOpaque = true // Opaque views render faster
        view.backgroundColor = .white
        view.clipsToBounds = true // Prevents rendering outside bounds
    }
}

// CADisplayLink for 60fps animation
class AnimationController {
    var displayLink: CADisplayLink?

    func startAnimation() {
        displayLink = CADisplayLink(
            target: self,
            selector: #selector(updateAnimation)
        )
        displayLink?.preferredFramesPerSecond = 60
        displayLink?.add(to: .main, forMode: .common)
    }

    @objc func updateAnimation() {
        // Update frame
    }
}
```

**Android - Rendering Optimization**
```kotlin
class RenderingOptimizer {
    companion object {
        fun optimizeViewHierarchy(view: View) {
            // Use include instead of nested layouts
            // Flatten hierarchy

            view.apply {
                isDrawingCacheEnabled = true
                willNotDraw = false // Only if drawing content
            }
        }

        fun reduceOverdraw(view: View) {
            // Set background only where needed
            if (view.background == null) {
                view.setBackgroundColor(Color.WHITE)
            }
        }
    }
}

// Use SurfaceView for complex graphics
class GameSurfaceView : SurfaceView(context), SurfaceHolder.Callback {
    private var renderThread: RenderThread? = null

    override fun surfaceCreated(holder: SurfaceHolder) {
        renderThread = RenderThread(holder).apply {
            start()
        }
    }

    private class RenderThread(private val holder: SurfaceHolder) : Thread() {
        override fun run() {
            while (true) {
                val canvas = holder.lockCanvas() ?: continue
                try {
                    // Render at 60fps
                    Thread.sleep(16) // ~60fps
                } finally {
                    holder.unlockCanvasAndPost(canvas)
                }
            }
        }
    }
}

// Enable GPU rendering debug
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // In onCreate or manifest
        // android:hardwareAccelerated="true"
        setContentView(R.layout.activity_main)
    }
}
```

**React Native - Rendering Optimization**
```javascript
// Use react-native-screens for native navigation
import { enableScreens } from 'react-native-screens';
enableScreens();

// Optimize FlatList rendering
<FlatList
  data={items}
  renderItem={({ item }) => <OptimizedItem item={item} />}
  keyExtractor={item => item.id}
  removeClippedSubviews={true}
  maxToRenderPerBatch={10}
  updateCellsBatchingPeriod={50}
  getItemLayout={(data, index) => ({
    length: ITEM_HEIGHT,
    offset: ITEM_HEIGHT * index,
    index,
  })}
/>

// Memoize expensive components
const MemoizedItem = React.memo(({ item }) => (
  <Text>{item.title}</Text>
));
```

**Flutter - Rendering Performance**
```dart
class RenderingOptimizer {
  // Use RepaintBoundary for expensive widgets
  static Widget optimizedWidget() {
    return RepaintBoundary(
      child: ExpensiveWidget(),
    );
  }

  // Use ListView instead of Column for long lists
  static Widget optimizedList(List<Item> items) {
    return ListView.builder(
      itemCount: items.length,
      itemBuilder: (context, index) {
        return ListTile(title: Text(items[index].title));
      },
    );
  }

  // Profile performance with DevTools
  static void profileWidget() {
    debugPrintScheduleBuildFrames = true;
  }
}
```

---

## 7. App Size Optimization

### Tree Shaking, Asset Compression, and App Thinning

**iOS - App Size Optimization**
```swift
// Use app thinning in Xcode
// On Device Code Stripping: Yes
// Strip Swift Symbols: Yes
// Asset Slicing: Enabled

class AssetManager {
    // Compress images in Assets.xcassets
    // Use WebP format where available

    // On-demand resources
    static func loadOnDemandAssets() {
        let request = NSBundleResourceRequest(tags: ["feature"])
        request.loadingPriority = NSBundleResourceRequestLoadingPriorityMax
        request.beginAccessingResources { error in
            // Assets loaded
        }
    }
}
```

**Android - App Size Optimization**
```kotlin
android {
    bundle {
        density.enableSplit = true
        abi.enableSplit = true
        language.enableSplit = true
    }

    packagingOptions {
        exclude 'META-INF/proguard/androidx-*.pro'
    }
}

// ProGuard/R8 configuration
-dontwarn com.example.**
-keep class com.example.model.** { *; }
-keepclassmembers class * {
    public static <fields>;
}

// Use Play Feature Delivery
class DynamicFeatureLoader {
    fun requestFeature(featureName: String) {
        val splitInstallManager = SplitInstallManagerFactory.create(context)
        val request = SplitInstallRequest.newBuilder()
            .addModule(featureName)
            .build()

        splitInstallManager.startInstall(request)
    }
}
```

**React Native - Bundle Optimization**
```bash
# Tree shaking - remove unused code
npm run build -- --mode production

# Analyze bundle size
npm install --save-dev react-native-bundle-visualizer
react-native-bundle-visualizer --entry-file index.js
```

**Flutter - App Size Optimization**
```yaml
# pubspec.yaml
# Remove unused dependencies

# Build with --split-per-abi for smaller downloads
flutter build apk --split-per-abi

# Analyze app size
flutter build ios --analyze-size
```

---

## 8. Lazy Loading Strategies

**iOS - Lazy Loading**
```swift
class LazyImageLoader {
    func loadImage(url: URL, completion: @escaping (UIImage?) -> Void) {
        DispatchQueue.global(qos: .userInitiated).async {
            if let data = try? Data(contentsOf: url),
               let image = UIImage(data: data) {
                DispatchQueue.main.async {
                    completion(image)
                }
            }
        }
    }
}

// Lazy table view loading
class TableViewController: UITableViewController {
    private var images: [UIImage?] = Array(repeating: nil, count: 100)

    override func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "cell", for: indexPath)

        if images[indexPath.row] == nil {
            loadImage(at: indexPath)
        }

        return cell
    }
}
```

**Android - Lazy Loading with Coil**
```kotlin
class LazyImageAdapter : RecyclerView.Adapter<ImageViewHolder>() {
    override fun onBindViewHolder(holder: ImageViewHolder, position: Int) {
        val imageUrl = items[position].imageUrl

        holder.imageView.load(imageUrl) {
            crossfade(300)
            placeholder(R.drawable.placeholder)
        }
    }
}
```

**React Native - Lazy Loading**
```javascript
function LazyImage({ url }) {
  const [loading, setLoading] = useState(true);

  return (
    <View>
      {loading && <ActivityIndicator />}
      <Image
        source={{ uri: url }}
        onLoadEnd={() => setLoading(false)}
      />
    </View>
  );
}
```

**Flutter - Lazy Loading**
```dart
class LazyImageWidget extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Image.network(
      url,
      loadingBuilder: (context, child, loadingProgress) {
        if (loadingProgress == null) return child;
        return CircularProgressIndicator();
      },
    );
  }
}
```

---

## 9. Database Query Optimization

### Indexing and Query Performance

**iOS - Core Data Optimization**
```swift
// Create indexes in data model
extension NSEntityDescription {
    static func createIndexes() {
        let fetchRequest: NSFetchRequest<NSFetchRequestExpression> = NSFetchRequest()
        // Add indexes in xcdatamodeld file
    }
}

// Optimize fetch requests
class DataManager {
    func fetchOptimized() -> [User] {
        let fetchRequest: NSFetchRequest<User> = User.fetchRequest()
        fetchRequest.predicate = NSPredicate(format: "age > 18")
        fetchRequest.returnsObjectsAsFaults = false
        fetchRequest.fetchBatchSize = 20

        return try! managedObjectContext.fetch(fetchRequest)
    }
}
```

**Android - Room Database Optimization**
```kotlin
@Entity(indices = [Index("userId"), Index("email", unique = true)])
data class User(
    @PrimaryKey val id: Int,
    val userId: String,
    val email: String
)

@Dao
interface UserDao {
    @Query("SELECT * FROM user WHERE userId = :userId")
    suspend fun getUserById(userId: String): User

    @Query("SELECT * FROM user WHERE age > :age")
    fun getUsersOlderThan(age: Int): Flow<List<User>>
}

// Use connection pooling
@Database(entities = [User::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
}
```

**React Native - Database Optimization**
```javascript
// SQLite with better-sqlite3
import Database from 'better-sqlite3';

const db = new Database('app.db');

// Create indexes
db.exec('CREATE INDEX idx_userId ON users(userId)');
db.exec('CREATE INDEX idx_email ON users(email) UNIQUE');

// Use prepared statements
const stmt = db.prepare('SELECT * FROM users WHERE userId = ?');
const user = stmt.get(userId);
```

**Flutter - Database Optimization**
```dart
class UserDatabase {
  Future<void> createIndexes() async {
    await database.execute(
      'CREATE INDEX idx_userId ON users(userId)'
    );
    await database.execute(
      'CREATE UNIQUE INDEX idx_email ON users(email)'
    );
  }

  Future<User> getUserById(String userId) async {
    final result = await database.query(
      'users',
      where: 'userId = ?',
      whereArgs: [userId],
    );

    return User.fromMap(result.first);
  }
}
```

---

## 10. Image Loading Libraries

**iOS - Kingfisher**
```swift
import Kingfisher

class ImageViewController: UIViewController {
    @IBOutlet weak var imageView: UIImageView!

    func loadImage() {
        let url = URL(string: "https://example.com/image.jpg")!

        imageView.kf.setImage(
            with: url,
            placeholder: UIImage(named: "placeholder"),
            options: [
                .cacheOriginalImage,
                .scaleFactor(UIScreen.main.scale),
                .processor(ResizingImageProcessor(referenceSize: CGSize(width: 200, height: 200)))
            ],
            completionHandler: { result in
                switch result {
                case .success: print("Image loaded")
                case .failure(let error): print("Error: \(error)")
                }
            }
        )
    }
}
```

**Android - Glide and Coil**
```kotlin
// Glide
Glide.with(context)
    .load("https://example.com/image.jpg")
    .placeholder(R.drawable.placeholder)
    .error(R.drawable.error)
    .diskCacheStrategy(DiskCacheStrategy.ALL)
    .into(imageView)

// Coil (modern alternative)
imageView.load("https://example.com/image.jpg") {
    crossfade(true)
    placeholder(R.drawable.placeholder)
    transformations(RoundedCornersTransformation(8.dp))
}
```

**React Native - react-native-fast-image**
```javascript
import FastImage from 'react-native-fast-image';

export default function ImageComponent() {
  return (
    <FastImage
      source={{
        uri: 'https://example.com/image.jpg',
        priority: FastImage.priority.high,
      }}
      style={{ width: 200, height: 200 }}
      resizeMode={FastImage.resizeMode.contain}
    />
  );
}
```

**Flutter - CachedNetworkImage**
```dart
import 'package:cached_network_image/cached_network_image.dart';

CachedNetworkImage(
  imageUrl: "https://example.com/image.jpg",
  placeholder: (context, url) => CircularProgressIndicator(),
  errorWidget: (context, url, error) => Icon(Icons.error),
  memCacheHeight: 400,
  memCacheWidth: 400,
)
```

---

## 11. Scroll Performance Optimization

**iOS - UITableView and UICollectionView**
```swift
class OptimizedTableViewController: UITableViewController {
    override func viewDidLoad() {
        super.viewDidLoad()

        tableView.rowHeight = UITableView.automaticDimension
        tableView.estimatedRowHeight = 100

        // Disable unnecessary features
        tableView.separatorStyle = .none
    }

    override func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "Cell", for: indexPath)
        configureCell(cell, for: indexPath)
        return cell
    }

    private func configureCell(_ cell: UITableViewCell, for indexPath: IndexPath) {
        // Reuse cell properly
    }
}
```

**Android - RecyclerView Optimization**
```kotlin
class OptimizedAdapter : RecyclerView.Adapter<ViewHolder>() {
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        return ViewHolder(LayoutInflater.from(parent.context).inflate(R.layout.item, parent, false))
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(items[position])
    }
}

// Configure RecyclerView
recyclerView.apply {
    setHasFixedSize(true)
    setItemViewCacheSize(20)
    recycledViewPool.setMaxRecycledViews(0, 20)
}
```

**React Native - FlatList**
```javascript
<FlatList
  data={items}
  keyExtractor={item => item.id}
  renderItem={({ item }) => <Item item={item} />}
  getItemLayout={(data, index) => ({
    length: ITEM_HEIGHT,
    offset: ITEM_HEIGHT * index,
    index,
  })}
  removeClippedSubviews={true}
  maxToRenderPerBatch={10}
  updateCellsBatchingPeriod={50}
  initialNumToRender={10}
/>
```

**Flutter - ListView and LazyColumn**
```dart
ListView.builder(
  itemCount: items.length,
  itemBuilder: (context, index) {
    return ListTile(
      title: Text(items[index].title),
    );
  },
)

// Or use CustomScrollView with SliverLists
CustomScrollView(
  slivers: [
    SliverAppBar(
      pinned: true,
      title: Text('Scroll Performance'),
    ),
    SliverList(
      delegate: SliverChildBuilderDelegate(
        (context, index) => ListTile(title: Text('Item $index')),
        childCount: items.length,
      ),
    ),
  ],
)
```

---

## 12. Profiling Tools

### iOS - Instruments
```swift
// Use Xcode Instruments
// - Core Animation: Check 60fps rendering
// - Memory Graph: Detect memory leaks
// - System Trace: Analyze thread performance
// - Network: Profile network requests

class ProfiledClass {
    func profiledMethod() {
        // Code to profile
        // Add breakpoints and use Instruments
    }
}

// Enable metrics collection
import MetricKit

class MetricsHandler: NSObject, MetricKitManagerDelegate {
    override init() {
        super.init()
        MXMetricManager.shared.add(self)
    }

    func didReceive(_ payloads: [MXMetricPayload]) {
        for payload in payloads {
            print("App launch time: \(payload.applicationLaunchMetrics?.histogrammedTimeToFirstDraw)")
        }
    }
}
```

### Android - Android Profiler
```kotlin
// Android Profiler shows:
// - CPU usage
// - Memory allocation
// - Network traffic
// - Energy consumption

class ProfiledActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Record method traces
        Debug.startMethodTracing("profile")
        // ... code to profile ...
        Debug.stopMethodTracing()
    }
}

// Enable StrictMode for development
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        if (BuildConfig.DEBUG) {
            StrictMode.setThreadPolicy(
                StrictMode.ThreadPolicy.Builder()
                    .detectDiskReads()
                    .detectDiskWrites()
                    .penaltyLog()
                    .build()
            )
        }
    }
}
```

### React Native - Flipper
```bash
# Install Flipper
npm install --save-dev flipper

# Built-in Flipper plugins provide:
# - React DevTools
# - Network Inspector
# - Database Browser
# - Logs

# Enable in your app
import { initializeFlipper } from 'react-native-flipper';

if (__DEV__) {
  initializeFlipper(() => {
    // Connection established
  });
}
```

### Flutter - DevTools
```bash
# Launch DevTools
flutter pub global activate devtools
devtools

# Or from VS Code command palette: "Open DevTools"

# Features:
# - Widget Inspector
# - Performance tab (60fps timeline)
# - Memory profiler
# - Network requests
# - Logging

import 'package:flutter/foundation.dart';

void main() {
  if (kDebugMode) {
    // Enable verbose logging
    debugPrint('Debug mode enabled');
  }
  runApp(MyApp());
}
```

---

## Performance Checklist

- [ ] App startup time < 2 seconds (cold start)
- [ ] 60fps maintained during scrolling
- [ ] Memory usage < 100MB (baseline)
- [ ] No memory leaks (profile regularly)
- [ ] Network requests batched when possible
- [ ] Images compressed and cached
- [ ] Database queries indexed
- [ ] App size < 100MB
- [ ] Battery drain < 5% per hour (idle)
- [ ] No ANR (Application Not Responding) errors
- [ ] Background tasks properly scheduled
- [ ] Low power mode optimizations implemented
