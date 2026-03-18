# Kotlin Multiplatform (KMP)

## Table of Contents

- [Overview & Architecture](#overview--architecture)
- [Build Configuration](#build-configuration)
- [expect/actual Pattern](#expectactual-pattern)
- [Networking with Ktor](#networking-with-ktor)
- [Data Persistence with SQLDelight](#data-persistence-with-sqldelight)
- [Dependency Injection with Koin](#dependency-injection-with-koin)
- [Consuming KMP from Swift (iOS)](#consuming-kmp-from-swift-ios)
- [Compose Multiplatform](#compose-multiplatform)
- [Testing Shared Code](#testing-shared-code)
- [KMP vs Other Cross-Platform Approaches](#kmp-vs-other-cross-platform-approaches)

## Overview & Architecture

Kotlin Multiplatform allows sharing business logic across iOS, Android, web, and desktop while keeping native UI on each platform. Unlike cross-platform UI frameworks, KMP shares the **logic layer** and lets each platform use its native UI toolkit.

```
┌─────────────────────────────────────────────┐
│              Shared Kotlin Code              │
│  ┌─────────┬──────────┬──────────────────┐  │
│  │ Models  │ Use Cases│  Repositories    │  │
│  │ DTOs    │ Business │  Data Sources    │  │
│  │ Enums   │ Logic    │  API Clients     │  │
│  └─────────┴──────────┴──────────────────┘  │
│         expect/actual declarations           │
├─────────────────┬───────────────────────────┤
│   Android       │         iOS               │
│  Jetpack Compose│     SwiftUI/UIKit         │
│  ViewModel      │     @Observable           │
│  Hilt DI        │     Swift Concurrency     │
└─────────────────┴───────────────────────────┘
```

### Project Structure

```
my-kmp-app/
├── shared/                          # Shared KMP module
│   ├── src/
│   │   ├── commonMain/kotlin/       # Shared code
│   │   │   ├── data/
│   │   │   │   ├── api/ApiClient.kt
│   │   │   │   ├── db/DatabaseDriver.kt
│   │   │   │   └── repository/UserRepository.kt
│   │   │   ├── domain/
│   │   │   │   ├── model/User.kt
│   │   │   │   └── usecase/GetUsersUseCase.kt
│   │   │   └── di/SharedModule.kt
│   │   ├── commonTest/kotlin/       # Shared tests
│   │   ├── androidMain/kotlin/      # Android-specific implementations
│   │   ├── iosMain/kotlin/          # iOS-specific implementations
│   │   └── desktopMain/kotlin/      # Desktop-specific (optional)
│   └── build.gradle.kts
├── androidApp/                      # Android app
│   ├── src/main/
│   │   ├── kotlin/com/example/
│   │   │   ├── ui/
│   │   │   └── MainActivity.kt
│   │   └── AndroidManifest.xml
│   └── build.gradle.kts
├── iosApp/                          # iOS app (Xcode project)
│   ├── iosApp/
│   │   ├── ContentView.swift
│   │   └── iOSApp.swift
│   └── iosApp.xcodeproj
└── build.gradle.kts
```

---

## Build Configuration

### Gradle Setup (shared/build.gradle.kts)

```kotlin
plugins {
    kotlin("multiplatform")
    kotlin("plugin.serialization")
    id("com.android.library")
    id("app.cash.sqldelight")
}

kotlin {
    androidTarget {
        compilations.all {
            kotlinOptions { jvmTarget = "17" }
        }
    }

    listOf(iosX64(), iosArm64(), iosSimulatorArm64()).forEach {
        it.binaries.framework {
            baseName = "shared"
            isStatic = true
        }
    }

    sourceSets {
        val commonMain by getting {
            dependencies {
                implementation("io.ktor:ktor-client-core:2.3.12")
                implementation("io.ktor:ktor-client-content-negotiation:2.3.12")
                implementation("io.ktor:ktor-serialization-kotlinx-json:2.3.12")
                implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.8.1")
                implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.7.1")
                implementation("org.jetbrains.kotlinx:kotlinx-datetime:0.6.0")
                implementation("app.cash.sqldelight:runtime:2.0.2")
                implementation("app.cash.sqldelight:coroutines-extensions:2.0.2")
                implementation("io.insert-koin:koin-core:3.5.6")
            }
        }
        val commonTest by getting {
            dependencies {
                implementation(kotlin("test"))
                implementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.8.1")
            }
        }
        val androidMain by getting {
            dependencies {
                implementation("io.ktor:ktor-client-okhttp:2.3.12")
                implementation("app.cash.sqldelight:android-driver:2.0.2")
            }
        }
        val iosMain by creating {
            dependsOn(commonMain)
            dependencies {
                implementation("io.ktor:ktor-client-darwin:2.3.12")
                implementation("app.cash.sqldelight:native-driver:2.0.2")
            }
        }
    }
}

sqldelight {
    databases {
        create("AppDatabase") {
            packageName.set("com.example.db")
        }
    }
}
```

---

## expect/actual Pattern

The `expect`/`actual` mechanism lets you define a common API and provide platform-specific implementations.

### Platform Abstraction

```kotlin
// commonMain — expect declaration
expect class PlatformContext

expect fun getPlatformName(): String

expect class SecureStorage(context: PlatformContext) {
    fun saveToken(key: String, value: String)
    fun getToken(key: String): String?
    fun deleteToken(key: String)
}

// androidMain — actual implementation
actual typealias PlatformContext = android.content.Context

actual fun getPlatformName(): String = "Android ${android.os.Build.VERSION.RELEASE}"

actual class SecureStorage actual constructor(private val context: PlatformContext) {
    private val prefs = EncryptedSharedPreferences.create(
        context, "secure_prefs",
        MasterKey.Builder(context).setKeyScheme(MasterKey.KeyScheme.AES256_GCM).build(),
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )

    actual fun saveToken(key: String, value: String) { prefs.edit().putString(key, value).apply() }
    actual fun getToken(key: String): String? = prefs.getString(key, null)
    actual fun deleteToken(key: String) { prefs.edit().remove(key).apply() }
}

// iosMain — actual implementation
import platform.Foundation.NSUserDefaults
import platform.Security.*

actual class PlatformContext

actual fun getPlatformName(): String = "iOS ${platform.UIKit.UIDevice.currentDevice.systemVersion}"

actual class SecureStorage actual constructor(context: PlatformContext) {
    actual fun saveToken(key: String, value: String) {
        val query = mapOf<Any?, Any?>(
            kSecClass to kSecClassGenericPassword,
            kSecAttrAccount to key,
            kSecValueData to value.encodeToByteArray().toNSData()
        )
        SecItemDelete(query.toCFDictionary())
        SecItemAdd(query.toCFDictionary(), null)
    }

    actual fun getToken(key: String): String? {
        // Keychain query implementation
        return null // simplified
    }

    actual fun deleteToken(key: String) {
        val query = mapOf<Any?, Any?>(
            kSecClass to kSecClassGenericPassword,
            kSecAttrAccount to key
        )
        SecItemDelete(query.toCFDictionary())
    }
}
```

---

## Networking with Ktor

```kotlin
// commonMain/data/api/ApiClient.kt
class ApiClient(engine: HttpClientEngine) {
    private val client = HttpClient(engine) {
        install(ContentNegotiation) {
            json(Json {
                ignoreUnknownKeys = true
                isLenient = true
                prettyPrint = false
            })
        }
        install(Logging) {
            level = LogLevel.HEADERS
        }
        install(HttpTimeout) {
            requestTimeoutMillis = 30_000
            connectTimeoutMillis = 10_000
        }
        defaultRequest {
            url("https://api.example.com/v1/")
            header("Accept", "application/json")
        }
    }

    suspend fun getUsers(): List<UserDto> =
        client.get("users").body()

    suspend fun getUser(id: String): UserDto =
        client.get("users/$id").body()

    suspend fun createUser(request: CreateUserRequest): UserDto =
        client.post("users") {
            contentType(ContentType.Application.Json)
            setBody(request)
        }.body()
}

// Platform-specific engine creation
// androidMain
actual fun createHttpEngine(): HttpClientEngine = OkHttp.create()

// iosMain
actual fun createHttpEngine(): HttpClientEngine = Darwin.create()
```

### Data Models with kotlinx.serialization

```kotlin
@Serializable
data class UserDto(
    val id: String,
    val name: String,
    val email: String,
    @SerialName("created_at")
    val createdAt: Instant,
    val avatar: String? = null,
)

@Serializable
data class CreateUserRequest(
    val name: String,
    val email: String,
)

@Serializable
sealed class ApiResult<out T> {
    @Serializable data class Success<T>(val data: T) : ApiResult<T>()
    @Serializable data class Error(val code: Int, val message: String) : ApiResult<Nothing>()
}
```

---

## Data Persistence with SQLDelight

### Schema Definition

```sql
-- shared/src/commonMain/sqldelight/com/example/db/User.sq

CREATE TABLE User (
    id TEXT NOT NULL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    avatar_url TEXT,
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL
);

-- Named queries become type-safe Kotlin functions
selectAll:
SELECT * FROM User ORDER BY name ASC;

selectById:
SELECT * FROM User WHERE id = ?;

insert:
INSERT OR REPLACE INTO User(id, name, email, avatar_url, created_at, updated_at)
VALUES (?, ?, ?, ?, ?, ?);

deleteById:
DELETE FROM User WHERE id = ?;

searchByName:
SELECT * FROM User WHERE name LIKE '%' || ? || '%' ORDER BY name ASC;
```

### Driver Setup (expect/actual)

```kotlin
// commonMain
expect class DatabaseDriverFactory {
    fun createDriver(): SqlDriver
}

fun createDatabase(driverFactory: DatabaseDriverFactory): AppDatabase {
    val driver = driverFactory.createDriver()
    return AppDatabase(driver)
}

// androidMain
actual class DatabaseDriverFactory(private val context: Context) {
    actual fun createDriver(): SqlDriver =
        AndroidSqliteDriver(AppDatabase.Schema, context, "app.db")
}

// iosMain
actual class DatabaseDriverFactory {
    actual fun createDriver(): SqlDriver =
        NativeSqliteDriver(AppDatabase.Schema, "app.db")
}
```

### Repository with Flow

```kotlin
class UserRepository(
    private val api: ApiClient,
    private val db: AppDatabase,
) {
    // Reactive query — emits whenever DB changes
    fun observeUsers(): Flow<List<User>> =
        db.userQueries.selectAll()
            .asFlow()
            .mapToList(Dispatchers.Default)
            .map { rows -> rows.map { it.toDomain() } }

    suspend fun refreshUsers(): Result<Unit> = runCatching {
        val remote = api.getUsers()
        db.transaction {
            remote.forEach { dto ->
                db.userQueries.insert(
                    id = dto.id,
                    name = dto.name,
                    email = dto.email,
                    avatar_url = dto.avatar,
                    created_at = dto.createdAt.toEpochMilliseconds(),
                    updated_at = Clock.System.now().toEpochMilliseconds()
                )
            }
        }
    }

    suspend fun getUser(id: String): User? =
        db.userQueries.selectById(id).executeAsOneOrNull()?.toDomain()
}
```

---

## Dependency Injection with Koin

```kotlin
// commonMain/di/SharedModule.kt
val sharedModule = module {
    single { ApiClient(createHttpEngine()) }
    single { createDatabase(get()) }
    single { UserRepository(get(), get()) }
    single { GetUsersUseCase(get()) }
}

// androidMain/di/AndroidModule.kt
val androidModule = module {
    single { DatabaseDriverFactory(get()) }
    single<PlatformContext> { get<Context>() as PlatformContext }
}

// Android Application
class MyApp : Application() {
    override fun onCreate() {
        super.onCreate()
        startKoin {
            androidContext(this@MyApp)
            modules(sharedModule, androidModule)
        }
    }
}

// iOS — initialize in Swift
@main
struct iOSApp: App {
    init() {
        KoinHelperKt.doInitKoin()
    }
    var body: some Scene {
        WindowGroup { ContentView() }
    }
}

// commonMain helper for iOS
fun initKoin() {
    startKoin {
        modules(sharedModule, iosModule)
    }
}
```

---

## Consuming KMP from Swift (iOS)

### Exposing Kotlin to Swift

```kotlin
// commonMain — ViewModel-like class for iOS consumption
class UserListViewModel(private val getUsers: GetUsersUseCase) {
    private val _state = MutableStateFlow(UserListState())
    val state: StateFlow<UserListState> = _state.asStateFlow()

    fun loadUsers() {
        _state.update { it.copy(isLoading = true) }
        CoroutineScope(Dispatchers.Main).launch {
            getUsers()
                .onSuccess { users ->
                    _state.update { it.copy(users = users, isLoading = false) }
                }
                .onFailure { error ->
                    _state.update { it.copy(error = error.message, isLoading = false) }
                }
        }
    }
}

data class UserListState(
    val users: List<User> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null,
)
```

### Swift Wrapper for SwiftUI

```swift
import shared  // The KMP framework

@Observable
class UserListViewModelWrapper {
    var users: [User] = []
    var isLoading = false
    var error: String?

    private let viewModel: UserListViewModel

    init() {
        let koin = KoinHelperKt.getKoin()
        viewModel = koin.get(objCClass: UserListViewModel.self) as! UserListViewModel
        observeState()
    }

    private func observeState() {
        // Collect Kotlin StateFlow in Swift
        FlowCollector(flow: viewModel.state) { [weak self] state in
            guard let state = state as? UserListState else { return }
            DispatchQueue.main.async {
                self?.users = state.users
                self?.isLoading = state.isLoading
                self?.error = state.error
            }
        }
    }

    func loadUsers() { viewModel.loadUsers() }
}

struct UserListView: View {
    @State private var viewModel = UserListViewModelWrapper()

    var body: some View {
        List(viewModel.users, id: \.id) { user in
            VStack(alignment: .leading) {
                Text(user.name).font(.headline)
                Text(user.email).font(.subheadline).foregroundStyle(.secondary)
            }
        }
        .overlay {
            if viewModel.isLoading { ProgressView() }
        }
        .task { viewModel.loadUsers() }
    }
}
```

---

## Compose Multiplatform

For teams that want shared UI as well as shared logic, Compose Multiplatform extends Jetpack Compose to iOS, desktop, and web.

```kotlin
// commonMain — shared Compose UI
@Composable
fun UserListScreen(viewModel: UserListViewModel) {
    val state by viewModel.state.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(title = { Text("Users") })
        }
    ) { padding ->
        if (state.isLoading) {
            Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator()
            }
        } else {
            LazyColumn(contentPadding = padding) {
                items(state.users) { user ->
                    ListItem(
                        headlineContent = { Text(user.name) },
                        supportingContent = { Text(user.email) },
                        leadingContent = {
                            AsyncImage(
                                model = user.avatarUrl,
                                contentDescription = null,
                                modifier = Modifier.size(40.dp).clip(CircleShape)
                            )
                        }
                    )
                }
            }
        }
    }
}
```

### Platform Entry Points

```kotlin
// androidMain
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                val viewModel: UserListViewModel = koinViewModel()
                UserListScreen(viewModel)
            }
        }
    }
}

// iosMain (Compose Multiplatform)
fun MainViewController(): UIViewController =
    ComposeUIViewController {
        MaterialTheme {
            val viewModel = remember { getKoin().get<UserListViewModel>() }
            UserListScreen(viewModel)
        }
    }
```

---

## Testing Shared Code

```kotlin
// commonTest
class UserRepositoryTest {
    private val fakeApi = FakeApiClient()
    private val fakeDb = createInMemoryDatabase()
    private val repository = UserRepository(fakeApi, fakeDb)

    @Test
    fun `refreshUsers stores remote data locally`() = runTest {
        fakeApi.setUsers(listOf(
            UserDto("1", "Alice", "alice@test.com", Clock.System.now())
        ))

        repository.refreshUsers()

        val users = repository.observeUsers().first()
        assertEquals(1, users.size)
        assertEquals("Alice", users[0].name)
    }

    @Test
    fun `observeUsers emits updates reactively`() = runTest {
        val emissions = mutableListOf<List<User>>()
        val job = launch { repository.observeUsers().take(2).toList(emissions) }

        repository.refreshUsers()
        job.join()

        assertEquals(2, emissions.size) // empty + loaded
    }
}
```

---

## KMP vs Other Cross-Platform Approaches

| Aspect | KMP (Logic Only) | Compose Multiplatform | Flutter | React Native |
|--------|------------------|-----------------------|---------|-------------|
| Shared Code | Business logic | Logic + UI | Everything | Everything |
| Native UI | Yes (Swift/Compose) | Compose everywhere | Custom renderer | Native bridge |
| iOS Experience | Truly native | Compose (good) | Custom (good) | Native-ish |
| Learning Curve | Kotlin + Swift | Kotlin | Dart | JS/React |
| Interop | Excellent | Good | Platform channels | Native modules |
| Performance | Native | Near-native | Near-native | Good |
| Maturity | Stable | Beta→Stable | Stable | Stable |
| Best For | Shared logic, native UX | Full sharing, Kotlin teams | Max code sharing | JS/React teams |

### When to Choose KMP

- You want **truly native UI** on each platform but don't want to duplicate business logic
- Your team knows **Kotlin and Swift** (or is willing to learn)
- You're building a **complex app** where business logic is a significant portion of the codebase
- You need **excellent native interop** (accessing platform APIs directly without bridges)
- You want to **incrementally adopt** shared code in an existing native app

### Common Pitfalls

1. **Coroutines ↔ Swift** — Kotlin coroutines don't map cleanly to Swift async/await. Use SKIE or KMP-NativeCoroutines library for better interop.
2. **Generics erasure** — Kotlin generics are erased in Objective-C/Swift interop. Use wrapper types.
3. **Memory management** — iOS uses ARC while KMP uses its own memory model. Avoid retain cycles with weak references.
4. **Binary framework size** — KMP frameworks can be large. Use static frameworks and strip unused code.
5. **Xcode integration** — Embedding the KMP framework requires build phase scripts. Use the KMP Xcode plugin or SPM integration.
