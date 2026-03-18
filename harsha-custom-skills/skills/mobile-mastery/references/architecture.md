# Mobile App Architecture Reference Guide

A comprehensive guide to modern mobile architecture patterns with practical Swift and Kotlin implementations.

## Table of Contents

- [1. Clean Architecture](#1-clean-architecture)
- [2. MVVM (Model-View-ViewModel)](#2-mvvm-model-view-viewmodel)
- [3. MVI (Model-View-Intent)](#3-mvi-model-view-intent)
- [4. Repository Pattern](#4-repository-pattern)
- [5. Modular Architecture](#5-modular-architecture)
- [6. Offline-First Architecture](#6-offline-first-architecture)
- [7. Dependency Injection](#7-dependency-injection)
- [8. Error Handling Strategies](#8-error-handling-strategies)
- [9. Feature Flags](#9-feature-flags)
- [10. Architecture Decision Matrix](#10-architecture-decision-matrix)

## 1. Clean Architecture

Clean Architecture separates code into independent layers with clear boundaries. The dependency rule states dependencies should only point inward.

### Core Layers

```
┌─────────────────────────────────┐
│    Presentation (UI)            │
├─────────────────────────────────┤
│    Domain (Business Logic)       │
├─────────────────────────────────┤
│    Data (Repositories)          │
├─────────────────────────────────┤
│    Framework/Drivers            │
└─────────────────────────────────┘
```

### Swift Implementation

```swift
// Domain Layer - Use Case
protocol FetchUserRepositoryProtocol {
    func getUser(id: String) async throws -> User
}

class FetchUserUseCase {
    private let repository: FetchUserRepositoryProtocol

    init(repository: FetchUserRepositoryProtocol) {
        self.repository = repository
    }

    func execute(userId: String) async throws -> User {
        return try await repository.getUser(id: userId)
    }
}

// Data Layer - Repository
class UserRepository: FetchUserRepositoryProtocol {
    private let remoteDataSource: UserRemoteDataSource
    private let localDataSource: UserLocalDataSource

    init(remote: UserRemoteDataSource, local: UserLocalDataSource) {
        self.remoteDataSource = remote
        self.localDataSource = local
    }

    func getUser(id: String) async throws -> User {
        do {
            let user = try await remoteDataSource.fetchUser(id: id)
            try await localDataSource.saveUser(user)
            return user
        } catch {
            return try await localDataSource.getUser(id: id)
        }
    }
}

// Presentation Layer
@MainActor
class UserViewModel: ObservableObject {
    @Published var user: User?
    @Published var isLoading = false
    @Published var error: String?

    private let fetchUserUseCase: FetchUserUseCase

    init(fetchUserUseCase: FetchUserUseCase) {
        self.fetchUserUseCase = fetchUserUseCase
    }

    func loadUser(id: String) {
        isLoading = true
        Task {
            do {
                self.user = try await fetchUserUseCase.execute(userId: id)
            } catch {
                self.error = error.localizedDescription
            }
            self.isLoading = false
        }
    }
}
```

### Kotlin Implementation

```kotlin
// Domain Layer - Use Case
interface FetchUserRepository {
    suspend fun getUser(id: String): User
}

class FetchUserUseCase(
    private val repository: FetchUserRepository
) {
    suspend operator fun invoke(userId: String): User {
        return repository.getUser(userId)
    }
}

// Data Layer - Repository
class UserRepository(
    private val remoteDataSource: UserRemoteDataSource,
    private val localDataSource: UserLocalDataSource
) : FetchUserRepository {
    override suspend fun getUser(id: String): User = withContext(Dispatchers.IO) {
        return@withContext try {
            val user = remoteDataSource.fetchUser(id)
            localDataSource.saveUser(user)
            user
        } catch (e: Exception) {
            localDataSource.getUser(id)
        }
    }
}

// Presentation Layer - ViewModel
class UserViewModel(
    private val fetchUserUseCase: FetchUserUseCase
) : ViewModel() {
    private val _uiState = MutableStateFlow<UiState>(UiState.Idle)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    fun loadUser(id: String) {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            try {
                val user = fetchUserUseCase(id)
                _uiState.value = UiState.Success(user)
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message ?: "Unknown error")
            }
        }
    }

    sealed class UiState {
        object Idle : UiState()
        object Loading : UiState()
        data class Success(val user: User) : UiState()
        data class Error(val message: String) : UiState()
    }
}
```

## 2. MVVM (Model-View-ViewModel)

MVVM separates UI from business logic through the ViewModel, enabling testability and reusability.

### SwiftUI Implementation

```swift
// Model
struct Product: Identifiable, Codable {
    let id: String
    let name: String
    let price: Double
    let description: String
}

// ViewModel
@MainActor
class ProductListViewModel: ObservableObject {
    @Published var products: [Product] = []
    @Published var isLoading = false
    @Published var selectedProduct: Product?
    @Published var searchText = ""

    private let productService: ProductService

    var filteredProducts: [Product] {
        searchText.isEmpty ? products :
            products.filter { $0.name.localizedCaseInsensitiveContains(searchText) }
    }

    init(productService: ProductService) {
        self.productService = productService
    }

    func fetchProducts() async {
        isLoading = true
        do {
            products = try await productService.getAllProducts()
        } catch {
            products = []
        }
        isLoading = false
    }

    func selectProduct(_ product: Product) {
        selectedProduct = product
    }
}

// View
struct ProductListView: View {
    @StateObject private var viewModel: ProductListViewModel

    init(productService: ProductService) {
        _viewModel = StateObject(
            wrappedValue: ProductListViewModel(productService: productService)
        )
    }

    var body: some View {
        NavigationStack {
            VStack {
                SearchBar(text: $viewModel.searchText)

                if viewModel.isLoading {
                    ProgressView()
                } else {
                    List(viewModel.filteredProducts) { product in
                        NavigationLink(
                            destination: ProductDetailView(product: product)
                        ) {
                            ProductRow(product: product)
                        }
                    }
                }
            }
            .navigationTitle("Products")
            .task {
                await viewModel.fetchProducts()
            }
        }
    }
}
```

### Jetpack Compose Implementation

```kotlin
// ViewModel
class ProductListViewModel(
    private val productService: ProductService
) : ViewModel() {
    private val _uiState = MutableStateFlow<List<Product>>(emptyList())
    val uiState: StateFlow<List<Product>> = _uiState.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    private val _searchQuery = MutableStateFlow("")
    val searchQuery: StateFlow<String> = _searchQuery.asStateFlow()

    val filteredProducts: Flow<List<Product>> = combine(
        _uiState,
        _searchQuery
    ) { products, query ->
        if (query.isEmpty()) products
        else products.filter { it.name.contains(query, ignoreCase = true) }
    }

    init {
        viewModelScope.launch {
            loadProducts()
        }
    }

    private suspend fun loadProducts() {
        _isLoading.value = true
        try {
            val products = productService.getAllProducts()
            _uiState.value = products
        } finally {
            _isLoading.value = false
        }
    }

    fun updateSearchQuery(query: String) {
        _searchQuery.value = query
    }
}

// Composable
@Composable
fun ProductListScreen(
    viewModel: ProductListViewModel = hiltViewModel()
) {
    val products by viewModel.filteredProducts.collectAsState(initial = emptyList())
    val isLoading by viewModel.isLoading.collectAsState()
    val searchQuery by viewModel.searchQuery.collectAsState()

    Column(modifier = Modifier.fillMaxSize()) {
        SearchBar(
            query = searchQuery,
            onQueryChange = { viewModel.updateSearchQuery(it) }
        )

        if (isLoading) {
            CircularProgressIndicator(modifier = Modifier.align(Alignment.CenterHorizontally))
        } else {
            LazyColumn {
                items(products, key = { it.id }) { product ->
                    ProductCard(product = product)
                }
            }
        }
    }
}
```

## 3. MVI (Model-View-Intent)

MVI implements unidirectional data flow where user intents produce model changes viewed by the UI.

### Swift Implementation

```swift
// Model
struct AppState {
    var products: [Product] = []
    var isLoading = false
    var error: String?
    var selectedFilter: ProductFilter = .all
}

// Intent
enum ProductIntent {
    case loadProducts
    case filterProducts(ProductFilter)
    case selectProduct(Product)
    case retryLoad
}

// State Reducer
class AppStateReducer {
    func reduce(state: inout AppState, intent: ProductIntent) {
        switch intent {
        case .loadProducts:
            state.isLoading = true
            state.error = nil

        case .filterProducts(let filter):
            state.selectedFilter = filter

        case .selectProduct:
            break // Handled elsewhere

        case .retryLoad:
            state.error = nil
            state.isLoading = true
        }
    }
}

// Store
@MainActor
class AppStore: ObservableObject {
    @Published private(set) var state: AppState = AppState()

    private let reducer: AppStateReducer
    private let middleware: AppMiddleware

    init(reducer: AppStateReducer, middleware: AppMiddleware) {
        self.reducer = reducer
        self.middleware = middleware
    }

    func dispatch(_ intent: ProductIntent) {
        Task {
            reducer.reduce(state: &state, intent: intent)

            if case .loadProducts = intent {
                do {
                    let products = try await middleware.fetchProducts()
                    state.products = products
                    state.isLoading = false
                } catch {
                    state.error = error.localizedDescription
                    state.isLoading = false
                }
            }
        }
    }
}

// Middleware
class AppMiddleware {
    private let productService: ProductService

    init(productService: ProductService) {
        self.productService = productService
    }

    func fetchProducts() async throws -> [Product] {
        return try await productService.getAllProducts()
    }
}
```

### Kotlin Implementation

```kotlin
// Model
data class AppState(
    val products: List<Product> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null,
    val selectedFilter: ProductFilter = ProductFilter.ALL
)

// Intent
sealed class ProductIntent {
    object LoadProducts : ProductIntent()
    data class FilterProducts(val filter: ProductFilter) : ProductIntent()
    data class SelectProduct(val product: Product) : ProductIntent()
    object RetryLoad : ProductIntent()
}

// Reducer
class AppStateReducer {
    fun reduce(state: AppState, intent: ProductIntent): AppState {
        return when (intent) {
            is ProductIntent.LoadProducts ->
                state.copy(isLoading = true, error = null)
            is ProductIntent.FilterProducts ->
                state.copy(selectedFilter = intent.filter)
            is ProductIntent.SelectProduct -> state
            is ProductIntent.RetryLoad ->
                state.copy(error = null, isLoading = true)
        }
    }
}

// Store
class AppStore(
    private val reducer: AppStateReducer,
    private val middleware: AppMiddleware
) : ViewModel() {
    private val _state = MutableStateFlow(AppState())
    val state: StateFlow<AppState> = _state.asStateFlow()

    fun dispatch(intent: ProductIntent) {
        val newState = reducer.reduce(_state.value, intent)
        _state.value = newState

        when (intent) {
            is ProductIntent.LoadProducts -> loadProducts()
            else -> {}
        }
    }

    private fun loadProducts() {
        viewModelScope.launch {
            try {
                val products = middleware.fetchProducts()
                _state.update { it.copy(products = products, isLoading = false) }
            } catch (e: Exception) {
                _state.update {
                    it.copy(error = e.message, isLoading = false)
                }
            }
        }
    }
}

// Middleware
class AppMiddleware(
    private val productService: ProductService
) {
    suspend fun fetchProducts(): List<Product> {
        return productService.getAllProducts()
    }
}
```

## 4. Repository Pattern

The Repository abstracts data sources and provides a clean API for data access.

### Swift Implementation

```swift
protocol LocalUserDataSource {
    func getUser(id: String) -> User?
    func saveUser(_ user: User)
    func clearUsers()
}

protocol RemoteUserDataSource {
    func fetchUser(id: String) async throws -> User
    func fetchUsers() async throws -> [User]
}

class UserRepository {
    private let local: LocalUserDataSource
    private let remote: RemoteUserDataSource
    private let cache = NSCache<NSString, CachedUser>()

    init(local: LocalUserDataSource, remote: RemoteUserDataSource) {
        self.local = local
        self.remote = remote
    }

    func getUser(id: String) async throws -> User {
        // Check memory cache
        if let cached = cache.object(forKey: id as NSString) {
            return cached.user
        }

        // Try remote
        do {
            let user = try await remote.fetchUser(id: id)
            local.saveUser(user)
            cache.setObject(CachedUser(user: user), forKey: id as NSString)
            return user
        } catch {
            // Fall back to local
            if let user = local.getUser(id: id) {
                cache.setObject(CachedUser(user: user), forKey: id as NSString)
                return user
            }
            throw RepositoryError.notFound
        }
    }

    func invalidateCache() {
        cache.removeAllObjects()
        local.clearUsers()
    }
}

class CachedUser {
    let user: User
    let timestamp: Date

    init(user: User) {
        self.user = user
        self.timestamp = Date()
    }
}

enum RepositoryError: LocalizedError {
    case notFound
    case syncFailed
}
```

### Kotlin Implementation

```kotlin
interface LocalUserDataSource {
    suspend fun getUser(id: String): User?
    suspend fun saveUser(user: User)
    suspend fun clearUsers()
}

interface RemoteUserDataSource {
    suspend fun fetchUser(id: String): User
    suspend fun fetchUsers(): List<User>
}

class UserRepository(
    private val local: LocalUserDataSource,
    private val remote: RemoteUserDataSource
) {
    private val cache = mutableMapOf<String, CachedUser>()

    suspend fun getUser(id: String): User = withContext(Dispatchers.IO) {
        // Check memory cache
        cache[id]?.takeIf { it.isValid }?.let { return@withContext it.user }

        return@withContext try {
            remote.fetchUser(id).also { user ->
                local.saveUser(user)
                cache[id] = CachedUser(user, System.currentTimeMillis())
            }
        } catch (e: Exception) {
            local.getUser(id)?.also { user ->
                cache[id] = CachedUser(user, System.currentTimeMillis())
            } ?: throw RepositoryException.NotFound()
        }
    }

    fun invalidateCache() {
        cache.clear()
        // Clear local DB in background
    }
}

data class CachedUser(
    val user: User,
    val timestamp: Long,
    val cacheTimeMs: Long = 5 * 60 * 1000
) {
    val isValid: Boolean
        get() = System.currentTimeMillis() - timestamp < cacheTimeMs
}

sealed class RepositoryException : Exception() {
    class NotFound : RepositoryException()
    class SyncFailed(message: String) : RepositoryException(message)
}
```

## 5. Modular Architecture

Organize code into feature modules with clear boundaries and explicit dependencies.

### Module Structure

```
app/
├── :app (Application)
├── :core
│   ├── :core:common
│   ├── :core:navigation
│   └── :core:network
├── :feature
│   ├── :feature:products
│   │   ├── data/
│   │   ├── domain/
│   │   └── presentation/
│   ├── :feature:cart
│   └── :feature:checkout
└── build.gradle.kts
```

### Kotlin Module Dependencies

```kotlin
// :feature:products/build.gradle.kts
dependencies {
    implementation(project(":core:common"))
    implementation(project(":core:network"))

    api(libs.kotlinx.coroutines)
    api(libs.jetpack.compose)
}

// :feature:cart/build.gradle.kts
dependencies {
    implementation(project(":core:common"))
    implementation(project(":feature:products")) // Only public API
}

// :app/build.gradle.kts
dependencies {
    implementation(project(":feature:products"))
    implementation(project(":feature:cart"))
    implementation(project(":feature:checkout"))
}
```

### Module Boundaries (Kotlin)

```kotlin
// :feature:products/src/main/kotlin/com/example/products/public/ProductApi.kt
// Only public types exposed
object ProductApi {
    fun createProductModule(context: Context): ProductModule {
        return ProductModule(context)
    }
}

// :feature:products/src/main/kotlin/com/example/products/ProductModule.kt
internal class ProductModule(private val context: Context) {
    internal fun productRepository(): ProductRepository = // ...
    internal fun productViewModel(): ProductViewModel = // ...
}

// Products internals never visible outside the module
```

## 6. Offline-First Architecture

Treat local database as source of truth, sync changes asynchronously.

### Swift Implementation

```swift
// Local DB Model
@Model
final class CachedProduct {
    @Attribute(.unique) let id: String
    var name: String
    var price: Double
    var lastSyncTime: Date
    var isSynced: Bool
}

@Model
final class SyncQueue {
    @Attribute(.unique) let id: String
    let action: String // "CREATE", "UPDATE", "DELETE"
    let resourceId: String
    let resourceType: String
    let payload: Data
    var isProcessing: Bool = false
    let createdAt: Date = Date()
}

class OfflineFirstProductRepository {
    @Environment(\.modelContext) var modelContext
    private let remote: RemoteProductDataSource

    func getProducts() async throws -> [Product] {
        // Always return local first
        let cached = try modelContext.fetch(FetchDescriptor<CachedProduct>())
        return cached.map { Product(from: $0) }
    }

    func syncProducts() async throws {
        // Sync local changes to server
        let queue = try modelContext.fetch(FetchDescriptor<SyncQueue>())

        for item in queue where !item.isProcessing {
            item.isProcessing = true
            do {
                try await processSyncItem(item)
                modelContext.delete(item)
            } catch {
                item.isProcessing = false
                throw error
            }
        }

        try modelContext.save()

        // Fetch fresh data
        let remoteProducts = try await remote.fetchProducts()
        for product in remoteProducts {
            try updateLocalProduct(product)
        }
    }

    private func processSyncItem(_ item: SyncQueue) async throws {
        switch item.action {
        case "CREATE":
            let product = try JSONDecoder().decode(Product.self, from: item.payload)
            _ = try await remote.createProduct(product)
        case "UPDATE":
            let product = try JSONDecoder().decode(Product.self, from: item.payload)
            _ = try await remote.updateProduct(product)
        case "DELETE":
            try await remote.deleteProduct(id: item.resourceId)
        default:
            break
        }
    }
}
```

### Kotlin Implementation

```kotlin
@Entity
data class CachedProduct(
    @PrimaryKey val id: String,
    val name: String,
    val price: Double,
    val lastSyncTime: Long,
    val isSynced: Boolean = true
)

@Entity
data class SyncQueueItem(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val action: String, // "CREATE", "UPDATE", "DELETE"
    val resourceId: String,
    val resourceType: String,
    val payload: String,
    val isProcessing: Boolean = false,
    val createdAt: Long = System.currentTimeMillis()
)

class OfflineFirstProductRepository(
    private val local: ProductDao,
    private val remote: RemoteProductDataSource,
    private val syncQueueDao: SyncQueueDao,
    private val scope: CoroutineScope
) {
    fun getProducts(): Flow<List<Product>> =
        local.getAllProducts().map { cached ->
            cached.map { Product.from(it) }
        }

    fun syncProducts() {
        scope.launch(Dispatchers.IO) {
            try {
                processSyncQueue()
                fetchRemoteUpdates()
            } catch (e: Exception) {
                Log.e("Sync", "Sync failed", e)
            }
        }
    }

    private suspend fun processSyncQueue() {
        val items = syncQueueDao.getPendingItems()

        for (item in items) {
            try {
                syncQueueDao.updateProcessing(item.id, true)
                processSyncItem(item)
                syncQueueDao.delete(item)
            } catch (e: Exception) {
                syncQueueDao.updateProcessing(item.id, false)
                throw e
            }
        }
    }

    private suspend fun processSyncItem(item: SyncQueueItem) {
        when (item.action) {
            "CREATE" -> {
                val product = Json.decodeFromString<Product>(item.payload)
                remote.createProduct(product)
            }
            "UPDATE" -> {
                val product = Json.decodeFromString<Product>(item.payload)
                remote.updateProduct(product)
            }
            "DELETE" -> remote.deleteProduct(item.resourceId)
        }
    }

    private suspend fun fetchRemoteUpdates() {
        val remote = remote.fetchProducts()
        local.insertProducts(remote.map { CachedProduct.from(it) })
    }
}
```

## 7. Dependency Injection

Manage object creation and dependency graphs efficiently.

### Swift Without Framework

```swift
// Service Locator (Simple DI)
class ServiceLocator {
    static let shared = ServiceLocator()

    private var services: [String: Any] = [:]

    func register<T>(_ service: T, forKey key: String) {
        services[key] = service
    }

    func resolve<T>(forKey key: String) -> T? {
        return services[key] as? T
    }
}

// Factory Pattern
class AppDependencies {
    static func makeUserViewModel() -> UserViewModel {
        let repository = makeUserRepository()
        let useCase = FetchUserUseCase(repository: repository)
        return UserViewModel(fetchUserUseCase: useCase)
    }

    private static func makeUserRepository() -> UserRepository {
        let remote = makeRemoteDataSource()
        let local = makeLocalDataSource()
        return UserRepository(remote: remote, local: local)
    }

    private static func makeRemoteDataSource() -> UserRemoteDataSource {
        return UserRemoteDataSourceImpl(
            httpClient: URLSession.shared
        )
    }

    private static func makeLocalDataSource() -> UserLocalDataSource {
        return UserLocalDataSourceImpl(
            database: AppDatabase.shared
        )
    }
}

// Usage
let viewModel = AppDependencies.makeUserViewModel()
```

### Kotlin with Hilt

```kotlin
@HiltViewModel
class UserViewModel @Inject constructor(
    private val fetchUserUseCase: FetchUserUseCase
) : ViewModel() {
    // ...
}

@Module
@InstallIn(SingletonComponent::class)
object RepositoryModule {
    @Singleton
    @Provides
    fun provideUserRepository(
        remote: UserRemoteDataSource,
        local: UserLocalDataSource
    ): UserRepository = UserRepository(remote, local)
}

@Module
@InstallIn(SingletonComponent::class)
object DataSourceModule {
    @Singleton
    @Provides
    fun provideRemoteDataSource(
        api: UserApi
    ): UserRemoteDataSource = UserRemoteDataSourceImpl(api)

    @Singleton
    @Provides
    fun provideLocalDataSource(
        database: AppDatabase
    ): UserLocalDataSource = UserLocalDataSourceImpl(database.userDao())
}

@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {
    @Singleton
    @Provides
    fun provideHttpClient(): OkHttpClient = OkHttpClient.Builder()
        .addInterceptor(LoggingInterceptor())
        .build()

    @Singleton
    @Provides
    fun provideUserApi(client: OkHttpClient): UserApi =
        Retrofit.Builder()
            .baseUrl(API_BASE_URL)
            .client(client)
            .addConverterFactory(Json.asConverterFactory("application/json".toMediaType()))
            .build()
            .create(UserApi::class.java)
}
```

## 8. Error Handling Strategies

Implement robust error handling with type safety.

### Swift Result Type

```swift
typealias AsyncResult<T> = Result<T, AppError>

enum AppError: LocalizedError {
    case network(NetworkError)
    case validation(String)
    case database(String)
    case unknown

    var errorDescription: String? {
        switch self {
        case .network(let error):
            return "Network error: \(error.localizedDescription)"
        case .validation(let message):
            return "Validation error: \(message)"
        case .database(let message):
            return "Database error: \(message)"
        case .unknown:
            return "An unknown error occurred"
        }
    }
}

enum NetworkError: LocalizedError {
    case invalidURL
    case requestFailed
    case decodingFailed
    case serverError(Int)

    var statusCode: Int? {
        if case .serverError(let code) = self { return code }
        return nil
    }
}

// Extension for mapping
extension NetworkError {
    static func from(_ error: Error) -> NetworkError {
        if let urlError = error as? URLError {
            return .requestFailed
        }
        return .unknown
    }
}
```

### Kotlin Sealed Classes

```kotlin
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val exception: Exception) : Result<Nothing>()
    object Loading : Result<Nothing>()
}

sealed class AppError(override val message: String = "") : Exception(message) {
    data class NetworkError(val code: Int, override val message: String) : AppError(message)
    data class ValidationError(override val message: String) : AppError(message)
    data class DatabaseError(override val message: String) : AppError(message)
    class UnknownError : AppError("Unknown error occurred")
}

// Error mapping utility
fun <T> Result<T>.getOrNull(): T? = when (this) {
    is Result.Success -> data
    is Result.Error -> null
    is Result.Loading -> null
}

fun <T, R> Result<T>.map(transform: (T) -> R): Result<R> = when (this) {
    is Result.Success -> Result.Success(transform(data))
    is Result.Error -> Result.Error(exception)
    is Result.Loading -> Result.Loading
}

// Usage
viewModelScope.launch {
    val result = fetchUserUseCase(userId)
    when (result) {
        is Result.Success -> _uiState.value = UiState.Content(result.data)
        is Result.Error -> {
            val error = when (result.exception) {
                is AppError.NetworkError -> "Network issue"
                is AppError.ValidationError -> "Validation failed"
                else -> "Unknown error"
            }
            _uiState.value = UiState.Error(error)
        }
        is Result.Loading -> _uiState.value = UiState.Loading
    }
}
```

## 9. Feature Flags

Control feature rollout and A/B testing through remote configuration.

### Swift Implementation

```swift
protocol FeatureFlagProvider {
    func isFeatureEnabled(_ feature: String) -> Bool
    func getRemoteConfig<T>(_ key: String, defaultValue: T) -> T
    func refreshConfig() async throws
}

class RemoteConfigFeatureFlagProvider: FeatureFlagProvider {
    private let remote: RemoteConfigService
    private var cache: [String: Any] = [:]

    func isFeatureEnabled(_ feature: String) -> Bool {
        return getRemoteConfig(feature, defaultValue: false)
    }

    func getRemoteConfig<T>(_ key: String, defaultValue: T) -> T {
        if let cached = cache[key] as? T {
            return cached
        }
        return defaultValue
    }

    func refreshConfig() async throws {
        let config = try await remote.fetchConfig()
        cache = config.toDictionary()
    }
}

// Usage
@MainActor
class FeatureViewModel: ObservableObject {
    @Published var showNewUI = false

    private let flagProvider: FeatureFlagProvider

    init(flagProvider: FeatureFlagProvider) {
        self.flagProvider = flagProvider
        self.showNewUI = flagProvider.isFeatureEnabled("new_ui_v2")
    }
}

// In View
struct ContentView: View {
    @StateObject private var viewModel: FeatureViewModel

    var body: some View {
        if viewModel.showNewUI {
            NewUIView()
        } else {
            LegacyUIView()
        }
    }
}
```

### Kotlin Implementation

```kotlin
interface FeatureFlagProvider {
    suspend fun isFeatureEnabled(feature: String): Boolean
    suspend fun <T> getRemoteConfig(key: String, defaultValue: T): T
    suspend fun refreshConfig()
}

class RemoteConfigFeatureFlagProvider(
    private val remote: RemoteConfigService,
    private val scope: CoroutineScope
) : FeatureFlagProvider {
    private val cache = mutableMapOf<String, Any>()
    private val _configUpdates = MutableSharedFlow<Unit>()
    val configUpdates: SharedFlow<Unit> = _configUpdates.asSharedFlow()

    override suspend fun isFeatureEnabled(feature: String): Boolean {
        return getRemoteConfig(feature, false)
    }

    override suspend fun <T> getRemoteConfig(key: String, defaultValue: T): T {
        @Suppress("UNCHECKED_CAST")
        cache[key]?.let { return it as T }
        return defaultValue
    }

    override suspend fun refreshConfig() {
        try {
            val config = remote.fetchConfig()
            cache.clear()
            cache.putAll(config)
            _configUpdates.emit(Unit)
        } catch (e: Exception) {
            Log.e("Config", "Failed to refresh config", e)
        }
    }
}

@HiltViewModel
class FeatureViewModel @Inject constructor(
    private val flagProvider: FeatureFlagProvider
) : ViewModel() {
    private val _showNewUI = MutableStateFlow(false)
    val showNewUI: StateFlow<Boolean> = _showNewUI.asStateFlow()

    init {
        viewModelScope.launch {
            _showNewUI.value = flagProvider.isFeatureEnabled("new_ui_v2")
        }
    }
}

// In Composable
@Composable
fun ContentScreen(viewModel: FeatureViewModel) {
    val showNewUI by viewModel.showNewUI.collectAsState()

    if (showNewUI) {
        NewUIScreen()
    } else {
        LegacyUIScreen()
    }
}
```

## 10. Architecture Decision Matrix

Choose the right architecture based on project characteristics.

### Decision Framework

| Factor | MVVM | Clean Arch | MVI | Modular |
|--------|------|-----------|-----|---------|
| **App Size** | Small-Medium | Medium-Large | Medium-Large | Large |
| **Team Size** | 1-3 | 3-8 | 3-8 | 5+ |
| **Complexity** | Low-Medium | High | High | High |
| **Testing Need** | Medium | High | High | High |
| **State Management** | Simple | Moderate | Complex | Varies |
| **Learning Curve** | Low | Medium | High | Medium |

### When to Use Each Pattern

**MVVM** - Best for:
- Smaller apps with straightforward features
- UI-focused applications
- Rapid prototyping
- Single developer teams

**Clean Architecture** - Best for:
- Large enterprise apps
- High testability requirements
- Teams with architectural guidelines
- Long-term maintenance needs

**MVI** - Best for:
- Complex state requirements
- Apps needing time-travel debugging
- Strict unidirectional data flow
- Redux-style state management

**Modular Architecture** - Best for:
- Multi-team development
- Feature-based scaling
- Independent feature releases
- Reusable components across apps

### Hybrid Approach Example

```
App Structure:
├── Modular organization (feature modules)
├── Each module uses Clean Architecture (layers)
├── Presentation layer uses MVVM (ViewModel + SwiftUI/Compose)
└── Complex state uses MVI pattern (Redux-like)
```

This maximizes benefits while maintaining flexibility:
- Module independence (Modular)
- Clear separation of concerns (Clean Architecture)
- Reactive UI updates (MVVM)
- Predictable state management (MVI)

### Complexity Progression

```
Start: MVVM
↓
Add: Repository Pattern (data abstraction)
↓
Add: Use Cases (domain logic)
↓
Migrate: Full Clean Architecture
↓
Enhance: MVI for complex features
↓
Scale: Modular architecture for multi-team
```

---

## Summary

Modern mobile architecture combines multiple patterns to achieve scalability, testability, and maintainability. Start simple with MVVM, add layers as complexity grows, and adopt modular architecture for team scaling. The key principle across all patterns is separation of concerns and unidirectional dependency flow.

Choose architecture based on your specific needs rather than following dogma. A pragmatic hybrid approach often serves production apps best.
