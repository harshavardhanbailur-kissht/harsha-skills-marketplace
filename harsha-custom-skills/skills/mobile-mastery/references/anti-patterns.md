# Mobile App Development Anti-Patterns Reference

A comprehensive catalog of common anti-patterns in mobile development with detection strategies, consequences, and correct implementations.

---

## Table of Contents

- [Architecture Anti-Patterns](#architecture-anti-patterns)
- [State Management Anti-Patterns](#state-management-anti-patterns)
- [Performance Anti-Patterns](#performance-anti-patterns)
- [Security Anti-Patterns](#security-anti-patterns)
- [UX Anti-Patterns](#ux-anti-patterns)
- [Testing Anti-Patterns](#testing-anti-patterns)
- [Platform-Specific Anti-Patterns](#platform-specific-anti-patterns)

---

## ARCHITECTURE ANTI-PATTERNS

### God Activity/ViewController — Severity: CRITICAL

**What**: A single Activity (Android) or ViewController (iOS) handles UI rendering, business logic, data fetching, caching, navigation, and lifecycle management. Thousands of lines of code in one class.

**Detect**: Activities/ViewControllers exceeding 500 lines; multiple responsibilities; mixing domain logic with UI code; direct database queries in controller.

**Why Bad**: Unmaintainable, untestable, prone to memory leaks, difficult to reuse logic, performance degradation, lifecycle-related crashes.

**Fix**: Decompose into ViewModel (state/logic), Repository (data access), UseCase (business rules), and View (UI only). Single Responsibility Principle.

**Wrong**:
```kotlin
class UserProfileActivity : AppCompatActivity() {
  override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    val db = UserDatabase.getInstance(this)
    val users = db.userDao().getAllUsers() // Blocking call on main thread!
    val filtered = users.filter { it.age > 18 }
    val sorted = filtered.sortedBy { it.name }
    updateUI(sorted)

    saveButton.setOnClickListener {
      val user = User(nameField.text.toString())
      db.userDao().insert(user) // Direct DB access, no error handling
      finish()
    }
  }
}
```

**Right**:
```kotlin
class UserProfileViewModel(private val userRepository: UserRepository) : ViewModel() {
  val users: StateFlow<List<User>> = userRepository.getAdultUsers()
    .stateIn(viewModelScope, SharingStarted.Lazily, emptyList())

  fun saveUser(name: String) = viewModelScope.launch {
    userRepository.insertUser(User(name)).fold(
      onSuccess = { /* Handle success */ },
      onFailure = { /* Handle error */ }
    )
  }
}

class UserProfileActivity : AppCompatActivity() {
  private val viewModel: UserProfileViewModel by viewModels()

  override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    lifecycleScope.launch {
      repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.users.collect { updateUI(it) }
      }
    }
  }
}
```

---

### Massive ViewModel — Severity: HIGH

**What**: ViewModel grows to handle multiple features, maintains state for unrelated concerns, accumulates business logic from multiple use cases.

**Detect**: ViewModels with 10+ public properties; multiple unrelated StateFlows; mixed responsibilities; business logic mixed with UI state.

**Why Bad**: Difficult testing, state conflicts, memory pressure, makes feature isolation impossible, code reuse across features fails.

**Fix**: Create feature-specific ViewModels. Use composition or separate ViewModels per screen section. Inject use cases cleanly.

**Wrong**:
```kotlin
class AppViewModel(
  private val userRepo: UserRepository,
  private val productRepo: ProductRepository,
  private val orderRepo: OrderRepository
) : ViewModel() {
  val users = MutableStateFlow<List<User>>(emptyList())
  val products = MutableStateFlow<List<Product>>(emptyList())
  val orders = MutableStateFlow<List<Order>>(emptyList())
  val cartItems = MutableStateFlow<List<CartItem>>(emptyList())
  val notifications = MutableStateFlow<List<Notification>>(emptyList())
  val selectedUser = MutableStateFlow<User?>(null)
  val selectedProduct = MutableStateFlow<Product?>(null)

  // 50+ functions mixing all concerns
  fun loadUsers() { /* ... */ }
  fun loadProducts() { /* ... */ }
  fun addToCart() { /* ... */ }
  fun checkout() { /* ... */ }
}
```

**Right**:
```kotlin
class UserListViewModel(private val getUsersUseCase: GetUsersUseCase) : ViewModel() {
  val users = getUsersUseCase().stateIn(viewModelScope, SharingStarted.Lazily, emptyList())
}

class ProductListViewModel(private val getProductsUseCase: GetProductsUseCase) : ViewModel() {
  val products = getProductsUseCase().stateIn(viewModelScope, SharingStarted.Lazily, emptyList())
}

class CartViewModel(private val cartUseCase: CartUseCase) : ViewModel() {
  val cartItems = cartUseCase.getCartItems()
    .stateIn(viewModelScope, SharingStarted.Lazily, emptyList())
}
```

---

### Anemic Domain Model — Severity: HIGH

**What**: Domain entities are plain data containers with getters/setters only. All business logic lives in repositories, use cases, or services, leaving entities powerless.

**Detect**: Entity classes with only properties and no methods; validation/business rules scattered across multiple files; Transaction-like objects lacking behavior.

**Why Bad**: Logic scattered and hard to find; entities don't enforce invariants; easy to create invalid states; difficult to test business rules in isolation.

**Fix**: Move business logic into entities. Use domain methods to enforce invariants. Entity changes should be intentional and validated.

**Wrong**:
```kotlin
data class Order(
  val id: String,
  val items: List<OrderItem>,
  val status: String,
  val total: Double,
  val discountPercent: Double
)

class OrderRepository {
  fun createOrder(items: List<OrderItem>): Order {
    val total = items.sumOf { it.price * it.quantity }
    val discount = if (items.size > 10) 0.1 else 0.0
    val finalTotal = total * (1 - discount)
    if (finalTotal < 0) throw IllegalArgumentException("Invalid total")
    return Order(UUID.randomUUID().toString(), items, "PENDING", finalTotal, discount)
  }

  fun updateOrderStatus(order: Order, newStatus: String) {
    if (order.status == "DELIVERED" && newStatus == "PENDING") {
      throw IllegalArgumentException("Cannot reverse delivered order")
    }
    order.status = newStatus // Mutable!
  }
}
```

**Right**:
```kotlin
class Order private constructor(
  val id: String,
  val items: List<OrderItem>,
  val status: OrderStatus,
  val discountPercent: Double
) {
  val total: Double
    get() = items.sumOf { it.price * it.quantity } * (1 - discountPercent)

  fun transitionTo(newStatus: OrderStatus): Result<Order> = runCatching {
    require(status.canTransitionTo(newStatus)) { "Cannot transition from $status to $newStatus" }
    Order(id, items, newStatus, discountPercent)
  }

  companion object {
    fun create(items: List<OrderItem>): Result<Order> = runCatching {
      require(items.isNotEmpty()) { "Order must have items" }
      val discount = if (items.size > 10) 0.1 else 0.0
      Order(UUID.randomUUID().toString(), items, OrderStatus.PENDING, discount)
    }
  }
}
```

---

### Repository Doing Too Much — Severity: HIGH

**What**: Repository handles caching, transformation, API calls, local DB, sync logic, and validation. No separation of concerns between data access and orchestration.

**Detect**: Repository methods doing multiple operations sequentially; mixing HTTP and database calls; retry logic inside repository; business transformation.

**Why Bad**: Hard to test (many dependencies); tight coupling to data sources; business rules in wrong layer; impossible to swap implementations.

**Fix**: Repository handles only data access. Use DataSource pattern. Extract sync and transformation logic to use cases.

**Wrong**:
```kotlin
class UserRepository(private val apiService: ApiService, private val database: UserDatabase) {
  suspend fun getUser(id: String): User {
    return try {
      val apiUser = apiService.fetchUser(id) // May fail
      val transformed = User(apiUser.id, apiUser.name.uppercase(), apiUser.email)
      database.userDao().insert(transformed)
      transformed
    } catch (e: Exception) {
      val cached = database.userDao().getUserById(id)
      if (cached != null) cached else throw e
    }
  }
}
```

**Right**:
```kotlin
class UserRepository(
  private val remoteDataSource: UserRemoteDataSource,
  private val localDataSource: UserLocalDataSource
) {
  suspend fun getUser(id: String): Result<User> = runCatching {
    remoteDataSource.fetchUser(id)
  }

  suspend fun cacheUser(user: User) = localDataSource.insert(user)
  suspend fun getCachedUser(id: String) = localDataSource.getUserById(id)
}

class GetUserUseCase(
  private val repository: UserRepository,
  private val userTransformer: UserTransformer
) {
  suspend operator fun invoke(id: String): Result<User> = repository.getUser(id)
    .onSuccess { repository.cacheUser(it) }
    .map { userTransformer.transform(it) }
    .recoverCatching {
      repository.getCachedUser(id) ?: throw it
    }
}
```

---

### Missing Error Boundary — Severity: CRITICAL

**What**: Exceptions in child components crash the entire app. No global error handler. Each screen handles errors independently (or not at all).

**Detect**: App crashes on unexpected errors; try-catch blocks everywhere or nowhere; no error state in UI; network failures crash UI.

**Why Bad**: Poor user experience; data loss; increased crash reports; unclear error messages; no recovery path.

**Fix**: Implement global error handler. Use Result types. Show error states in UI with recovery options.

**Wrong**:
```swift
class UserViewController: UIViewController {
  override func viewDidLoad() {
    super.viewDidLoad()
    Task {
      let users = try await userService.fetchUsers() // Throws - kills entire view
      updateUI(users)
    }
  }
}

class AppDelegate: UIResponder, UIApplicationDelegate {
  // No error handling at all
}
```

**Right**:
```swift
class AppDelegate: UIResponder, UIApplicationDelegate {
  func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
    setupErrorHandling()
    return true
  }

  private func setupErrorHandling() {
    let errorHandler = GlobalErrorHandler()
    setupUncaughtExceptionHandler(errorHandler)
  }
}

class UserViewController: UIViewController {
  @MainActor
  override func viewDidLoad() {
    super.viewDidLoad()
    Task {
      do {
        let users = try await userService.fetchUsers()
        updateUI(users)
      } catch {
        showError(error, onRetry: { self.viewDidLoad() })
      }
    }
  }
}

enum AppError: Error {
  case network(NetworkError)
  case parsing(DecodingError)
  case unknown(Error)

  var userMessage: String {
    switch self {
    case .network: return "Connection failed. Please try again."
    case .parsing: return "Data format error. Contact support."
    case .unknown: return "Something went wrong."
    }
  }
}
```

---

### Tight Coupling to Framework — Severity: HIGH

**What**: Business logic directly depends on Android/iOS framework classes. Domain models use framework types. Repository returns framework objects.

**Detect**: Domain classes importing android.* or UIKit; business logic calling Context/UIViewController directly; framework types in interfaces.

**Why Bad**: Code not testable without framework; logic can't be reused; framework updates require refactoring business code.

**Fix**: Use abstractions. Keep domain layer independent. Inject platform adapters.

**Wrong**:
```kotlin
class PaymentProcessor(private val context: Context) {
  fun processPayment(amount: Double): LiveData<PaymentResult> {
    val liveData = MutableLiveData<PaymentResult>()
    Thread {
      try {
        val result = callPaymentAPI(amount)
        liveData.postValue(PaymentResult.Success(result))
        Toast.makeText(context, "Payment successful", Toast.LENGTH_SHORT).show()
      } catch (e: Exception) {
        liveData.postValue(PaymentResult.Error(e))
      }
    }.start()
    return liveData
  }
}
```

**Right**:
```kotlin
interface PlatformLogger {
  fun logSuccess(message: String)
  fun logError(message: String)
}

class PaymentProcessor(private val logger: PlatformLogger) {
  fun processPayment(amount: Double): Flow<PaymentResult> = flow {
    try {
      val result = callPaymentAPI(amount)
      emit(PaymentResult.Success(result))
      logger.logSuccess("Payment successful")
    } catch (e: Exception) {
      emit(PaymentResult.Error(e))
      logger.logError(e.message ?: "Unknown error")
    }
  }
}

class AndroidLogger(private val context: Context) : PlatformLogger {
  override fun logSuccess(message: String) {
    Toast.makeText(context, message, Toast.LENGTH_SHORT).show()
  }

  override fun logError(message: String) {
    Toast.makeText(context, message, Toast.LENGTH_LONG).show()
  }
}
```

---

### Business Logic in UI Layer — Severity: CRITICAL

**What**: Validation, calculations, transformations, and business rules exist in Activities/ViewControllers/Composables instead of domain/use case layer.

**Detect**: Complex if-statements in UI code; calculations before rendering; validation before submission; state mutations in UI callbacks.

**Why Bad**: Logic duplicated across screens; untestable; tangled code; inconsistent behavior; UI changes break business rules.

**Fix**: Extract to use cases and domain models. UI layer only handles presentation.

**Wrong**:
```kotlin
@Composable
fun CheckoutScreen(viewModel: CheckoutViewModel) {
  var cartTotal by remember { mutableStateOf(0.0) }
  var discountAmount by remember { mutableStateOf(0.0) }

  LaunchedEffect(Unit) {
    viewModel.getCartItems().collect { items ->
      cartTotal = items.sumOf { it.price * it.quantity }
      discountAmount = if (cartTotal > 100) cartTotal * 0.1 else 0.0

      if (discountAmount < 0) discountAmount = 0.0
      if (cartTotal - discountAmount < 0) {
        // Error handling logic in UI
      }
    }
  }
}
```

**Right**:
```kotlin
class CalculatePriceUseCase(private val repository: CartRepository) {
  suspend operator fun invoke(items: List<CartItem>): Result<PriceBreakdown> = runCatching {
    val subtotal = items.sumOf { it.price * it.quantity }
    val discount = calculateDiscount(subtotal)
    val total = subtotal - discount
    require(total >= 0) { "Invalid total" }
    PriceBreakdown(subtotal, discount, total)
  }

  private fun calculateDiscount(subtotal: Double): Double =
    if (subtotal > 100) subtotal * 0.1 else 0.0
}

class CheckoutViewModel(private val calculatePriceUseCase: CalculatePriceUseCase) : ViewModel() {
  val priceBreakdown: StateFlow<PriceBreakdown> =
    priceUseCase().stateIn(viewModelScope, SharingStarted.Lazily, PriceBreakdown.ZERO)
}

@Composable
fun CheckoutScreen(viewModel: CheckoutViewModel) {
  val breakdown by viewModel.priceBreakdown.collectAsState()
  Text("Total: ${breakdown.total}")
}
```

---

### Circular Dependencies — Severity: HIGH

**What**: Module A depends on Module B, Module B depends on Module A. Or ViewModel depends on Repository that depends on ViewModel.

**Detect**: Compile errors about circular imports; constructor injection creating cycles; cross-module dependencies.

**Why Bad**: Impossible to test in isolation; unpredictable initialization order; difficult to reason about; architectural violation.

**Fix**: Introduce mediator/coordinator pattern. Dependency should flow in one direction only.

**Wrong**:
```kotlin
// Module A
class UserViewModel(val orderRepository: OrderRepository) {
  fun loadOrders() = orderRepository.getOrders()
}

// Module B
class OrderRepository(private val userViewModel: UserViewModel) {
  fun getOrders() {
    val user = userViewModel.currentUser // Circular!
    return fetchOrdersForUser(user)
  }
}
```

**Right**:
```kotlin
class UserStore {
  val currentUser: StateFlow<User?> = MutableStateFlow(null)
}

class UserViewModel(private val userStore: UserStore) {
  fun loadOrders() = orderRepository.getOrders(userStore.currentUser.value!!)
}

class OrderRepository(private val userStore: UserStore) {
  fun getOrders(user: User) = fetchOrdersForUser(user)
}
```

---

### Over-Engineering (Too Many Layers) — Severity: MEDIUM

**What**: Simple CRUD app has UseCase → Repository → DataSource → DAO → Service layers. Every interaction passes through 5 abstraction layers.

**Detect**: Simple operations requiring 4+ class instantiations; boilerplate exceeds business logic; unnecessary interfaces for single implementations.

**Why Bad**: Cognitive overhead; navigation difficulty; debugging maze; slow development.

**Fix**: Match architecture to complexity. Simple apps: ViewModel + Repository. Complex apps: add use cases/domain layer gradually.

**Wrong**:
```kotlin
// Just showing a list of 10 hardcoded items, yet:
// UserRemoteDataSource → UserDataSourceImpl
// UserRepository → UserRepositoryImpl
// GetUsersUseCase
// UserListViewModel
// UserListActivity
// 7 files for 10 items
```

**Right**:
```kotlin
// Simple case: ViewModel fetches directly
class UserListViewModel(private val repository: UserRepository) : ViewModel() {
  val users = repository.getUsers()
    .stateIn(viewModelScope, SharingStarted.Lazily, emptyList())
}

// Add complexity layer only when needed
```

---

### Missing Offline Handling — Severity: HIGH

**What**: App assumes constant connectivity. Network failures result in blank screens. No data caching or sync queue.

**Detect**: No cache layer; app shows errors on network failure instead of cached data; no offline indicator; no background sync.

**Why Bad**: Poor UX in poor connection; data loss; user frustration; business logic depends on network timing.

**Fix**: Cache all data locally. Queue mutations. Show cached data with "offline" indicator. Sync when online.

**Wrong**:
```kotlin
class ProductRepository(private val api: ProductApi) {
  suspend fun getProducts(): List<Product> {
    return api.fetchProducts() // Crashes if offline
  }
}
```

**Right**:
```kotlin
class ProductRepository(
  private val api: ProductApi,
  private val database: ProductDatabase,
  private val syncQueue: SyncQueue
) {
  fun getProducts(): Flow<List<Product>> = flow {
    // Try network first, emit cached if fails
    val cached = database.getProducts()
    emit(cached)

    try {
      val fresh = api.fetchProducts()
      database.insertAll(fresh)
      emit(fresh)
    } catch (e: Exception) {
      if (cached.isEmpty()) throw e
    }
  }

  suspend fun addProduct(product: Product) {
    syncQueue.enqueue(SyncAction.CreateProduct(product))
    database.insert(product)
  }
}
```

---

## STATE MANAGEMENT ANTI-PATTERNS

### Global State for Everything — Severity: CRITICAL

**What**: One global object or service holds all app state. Passed everywhere. Mutated from any component.

**Detect**: AppState/GlobalState objects; service locators with mutable properties; passing the entire app state to every function.

**Why Bad**: Race conditions; debugging nightmare; memory bloat; state conflicts; impossible to test; mutations from unexpected places.

**Fix**: Scope state to where it's needed. Use local state + dependency injection. State flows down, events up.

**Wrong**:
```kotlin
object AppState {
  var currentUser: User? = null
  var cartItems: MutableList<CartItem> = mutableListOf()
  var orders: MutableList<Order> = mutableListOf()
  var selectedFilter: String = ""

  fun addToCart(item: CartItem) {
    cartItems.add(item) // Mutation from anywhere!
  }
}

class ProductDetailActivity : AppCompatActivity() {
  fun onAddToCart(product: Product) {
    AppState.addToCart(CartItem(product)) // Global mutation
  }
}
```

**Right**:
```kotlin
class CartViewModel(private val repository: CartRepository) : ViewModel() {
  private val _cartItems = MutableStateFlow<List<CartItem>>(emptyList())
  val cartItems: StateFlow<List<CartItem>> = _cartItems.asStateFlow()

  fun addToCart(item: CartItem) = viewModelScope.launch {
    val result = repository.addToCart(item)
    if (result.isSuccess) {
      _cartItems.value = _cartItems.value + item
    }
  }
}

class ProductDetailActivity : AppCompatActivity() {
  private val cartViewModel: CartViewModel by viewModels()

  fun onAddToCart(product: Product) {
    cartViewModel.addToCart(CartItem(product))
  }
}
```

---

### Props Drilling Hell — Severity: MEDIUM

**What**: Passing props through 5+ levels of components that don't need them, just to reach a child that does.

**Detect**: Long parameter lists; same parameter in multiple function signatures; middle components taking unused parameters.

**Why Bad**: Fragile code; changing parameter breaks entire chain; unclear data flow; refactoring nightmare.

**Fix**: Use state management (ViewModels, Context, Redux-like state). Hoist state higher. Dependency injection.

**Wrong**:
```kotlin
@Composable
fun HomeScreen(user: User, onAddToCart: (CartItem) -> Unit, onUserUpdate: (User) -> Unit, cartItems: List<CartItem>) {
  ProductList(user, onAddToCart, onUserUpdate, cartItems)
}

@Composable
fun ProductList(user: User, onAddToCart: (CartItem) -> Unit, onUserUpdate: (User) -> Unit, cartItems: List<CartItem>) {
  ProductItem(user, onAddToCart, onUserUpdate, cartItems)
}

@Composable
fun ProductItem(user: User, onAddToCart: (CartItem) -> Unit, onUserUpdate: (User) -> Unit, cartItems: List<CartItem>) {
  Button(onClick = { onAddToCart(CartItem(product)) })
}
```

**Right**:
```kotlin
class ProductViewModel(private val cartUseCase: CartUseCase) : ViewModel() {
  fun addToCart(item: CartItem) = viewModelScope.launch {
    cartUseCase.addToCart(item)
  }
}

@Composable
fun HomeScreen() {
  val viewModel: ProductViewModel = viewModel()
  ProductList(viewModel)
}

@Composable
fun ProductList(viewModel: ProductViewModel) {
  ProductItem(viewModel)
}

@Composable
fun ProductItem(viewModel: ProductViewModel) {
  Button(onClick = { viewModel.addToCart(item) })
}
```

---

### Zombie Subscriptions — Severity: HIGH

**What**: Observers, listeners, or subscriptions not unsubscribed. Component destroyed but subscription still runs and references component.

**Detect**: Memory leaks in tests; Logcat warnings about undisposed observables; subscriptions outliving components.

**Why Bad**: Memory leaks; dangling references; crashes when subscription tries to update destroyed view; battery drain; data corruption.

**Fix**: Unsubscribe in lifecycle methods. Use Lifecycle-aware components. Use Flow with lifecycle scoping.

**Wrong**:
```kotlin
class UserFragment : Fragment() {
  private val viewModel: UserViewModel by viewModels()

  override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
    super.onViewCreated(view, savedInstanceState)

    viewModel.users.subscribe { users ->
      updateUI(users) // Never unsubscribed!
    }
  }
}

// Or RxJava style
class UserActivity : AppCompatActivity() {
  private val disposeBag = CompositeDisposable()

  override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)

    userRepository.getUsers()
      .subscribe(
        { updateUI(it) },
        { showError(it) }
      )
      // No disposal in onDestroy()
  }
}
```

**Right**:
```kotlin
class UserFragment : Fragment() {
  private val viewModel: UserViewModel by viewModels()

  override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
    super.onViewCreated(view, savedInstanceState)

    viewLifecycleOwner.lifecycleScope.launch {
      viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.users.collect { users ->
          updateUI(users)
        } // Automatically cancelled on STOPPED
      }
    }
  }
}

// RxJava proper disposal
class UserActivity : AppCompatActivity() {
  private val disposeBag = CompositeDisposable()

  override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)

    disposeBag.add(
      userRepository.getUsers()
        .subscribe(
          { updateUI(it) },
          { showError(it) }
        )
    )
  }

  override fun onDestroy() {
    disposeBag.dispose()
    super.onDestroy()
  }
}
```

---

### Derived State Stored Instead of Computed — Severity: MEDIUM

**What**: Calculate a derived value once and store it in state, instead of computing it on-demand from source state.

**Detect**: State with "_derived" suffix; computed values stored in MutableState; duplicate state that changes together.

**Why Bad**: Out-of-sync bugs; redundant memory; inconsistency; must update multiple places; violates DRY.

**Fix**: Use computed properties or derived flows. Compute on-access.

**Wrong**:
```kotlin
class CartViewModel : ViewModel() {
  val cartItems = MutableStateFlow<List<CartItem>>(emptyList())
  val totalPrice = MutableStateFlow(0.0) // Derived state!
  val itemCount = MutableStateFlow(0) // Derived state!

  fun addItem(item: CartItem) {
    cartItems.value = cartItems.value + item
    totalPrice.value = cartItems.value.sumOf { it.price * it.quantity } // Must update
    itemCount.value = cartItems.value.size // Must update
  }
}
```

**Right**:
```kotlin
class CartViewModel : ViewModel() {
  val cartItems = MutableStateFlow<List<CartItem>>(emptyList())

  val totalPrice: Flow<Double> = cartItems.map { items ->
    items.sumOf { it.price * it.quantity }
  }

  val itemCount: Flow<Int> = cartItems.map { it.size }

  fun addItem(item: CartItem) {
    cartItems.value = cartItems.value + item
    // Derived values computed automatically
  }
}
```

---

### State in Wrong Scope — Severity: HIGH

**What**: UI state (currentScreen, showDialog) stored in ViewModel. Or persistent state in local component state.

**Detect**: ViewModel managing UI navigation; navigation stack in StateFlow; savedInstanceState not persisting business data.

**Why Bad**: State lost on config change; UI state survives screen destruction; business logic depends on UI state; testability issues.

**Fix**: UI state in View layer. Business state in ViewModel. Persistent state in SavedStateHandle.

**Wrong**:
```kotlin
class AppViewModel : ViewModel() {
  val currentScreen = MutableStateFlow<Screen>(Screen.HOME)
  val showDialog = MutableStateFlow(false)
  val dialogMessage = MutableStateFlow("")
}

@Composable
fun App(viewModel: AppViewModel) {
  val currentScreen by viewModel.currentScreen.collectAsState()
  when (currentScreen) {
    is Screen.Home -> HomeScreen()
    is Screen.Details -> DetailsScreen()
  }
}
```

**Right**:
```kotlin
@Composable
fun App() {
  var currentScreen by remember { mutableStateOf<Screen>(Screen.HOME) }
  var showDialog by remember { mutableStateOf(false) }

  when (currentScreen) {
    is Screen.Home -> HomeScreen(onNavigate = { currentScreen = it })
    is Screen.Details -> DetailsScreen(onNavigate = { currentScreen = it })
  }
}

class UserViewModel(private val savedStateHandle: SavedStateHandle) : ViewModel() {
  val userId: StateFlow<String> =
    savedStateHandle.getStateFlow("userId", "")
  // Survives config change
}
```

---

### Mutating State Directly — Severity: CRITICAL

**What**: Direct mutation of collection state or data classes. `state.items.add(x)` instead of `state = state.copy(items = state.items + x)`.

**Detect**: Calling methods on state objects; mutable collections in state; state mutations outside setState/copy calls.

**Why Bad**: Recomposition doesn't trigger; race conditions; state becomes unpredictable; easy to corrupt; thread-unsafe.

**Fix**: Treat state as immutable. Always create new instances. Use copy() for data classes. Use += for collections.

**Wrong**:
```kotlin
class CartViewModel : ViewModel() {
  val cartItems = MutableStateFlow(mutableListOf<CartItem>())

  fun addItem(item: CartItem) {
    cartItems.value.add(item) // Direct mutation!
  }

  fun removeItem(index: Int) {
    cartItems.value.removeAt(index) // No recomposition!
  }
}
```

**Right**:
```kotlin
class CartViewModel : ViewModel() {
  val cartItems = MutableStateFlow<List<CartItem>>(emptyList())

  fun addItem(item: CartItem) {
    cartItems.value = cartItems.value + item // New list
  }

  fun removeItem(index: Int) {
    cartItems.value = cartItems.value.filterIndexed { i, _ -> i != index }
  }
}

data class User(val name: String, val email: String) {
  fun updateEmail(newEmail: String) = copy(email = newEmail)
}

val user = User("John", "old@example.com")
val updated = user.updateEmail("new@example.com") // New instance
```

---

### Race Conditions in Async State Updates — Severity: HIGH

**What**: Multiple async operations update state without synchronization. First request completes last, stale data overwrites fresh data.

**Detect**: Network requests updating same state; no request cancellation; timing-dependent bugs; flaky tests.

**Why Bad**: Stale data displayed; race-dependent crashes; unpredictable UI; data inconsistency.

**Fix**: Cancel previous requests. Use scope.launch with cancellation. Sequence updates properly. Track request ID.

**Wrong**:
```kotlin
class UserViewModel : ViewModel() {
  val userData = MutableStateFlow<User?>(null)

  fun loadUser(userId: String) = viewModelScope.launch {
    val user = api.getUser(userId)
    userData.value = user // Slow network might complete out of order
  }

  fun loadAllUsers() {
    for (id in userIds) {
      loadUser(id) // Multiple concurrent requests
    }
  }
}
```

**Right**:
```kotlin
class UserViewModel : ViewModel() {
  val userData = MutableStateFlow<User?>(null)
  private var loadingJob: Job? = null

  fun loadUser(userId: String) {
    loadingJob?.cancel() // Cancel previous
    loadingJob = viewModelScope.launch {
      val user = api.getUser(userId)
      userData.value = user
    }
  }
}

// Or using switchMap in Rx
val userData: Flow<User?> = userIdFlow
  .switchMap { userId ->
    api.getUser(userId).catch { emit(null) }
  }
```

---

### Over-Fetching (Loading Entire Entities) — Severity: MEDIUM

**What**: Load entire User entity when you only need the name. Load all Product fields when listing.

**Detect**: Network payload larger than displayed data; unused fields in DTO; loading 1000-field entities for simple display.

**Why Bad**: Bandwidth waste; battery drain; slower load times; large cache; memory pressure.

**Fix**: Use targeted queries. Return DTOs with only needed fields. Pagination for large datasets.

**Wrong**:
```kotlin
// API returns entire User object for a profile list
suspend fun getUsers(): List<User> // 30 fields per user

// UI only needs name and avatar
@Composable
fun UserListItem(user: User) {
  Text(user.name)
  Image(user.avatarUrl)
  // Ignoring 28 other fields
}
```

**Right**:
```kotlin
data class UserListItem(
  val id: String,
  val name: String,
  val avatarUrl: String
)

suspend fun getUserListItems(): List<UserListItem>

@Composable
fun UserListItem(item: UserListItem) {
  Text(item.name)
  Image(item.avatarUrl)
}
```

---

## PERFORMANCE ANTI-PATTERNS

### Unnecessary Re-Renders/Recompositions — Severity: HIGH

**What**: Composable recomposes every frame. Activity recreates views constantly. UI rebuilds when unrelated state changes.

**Detect**: Logcat "Recomposing" messages; profiler shows high composition count; layout inflation in callbacks.

**Why Bad**: Jank; ANR crashes; battery drain; CPU thrashing; poor animations.

**Fix**: Use key() in lists. Mark stable parameters. Memoize expensive computations. Scope state properly.

**Wrong**:
```kotlin
@Composable
fun UserList(users: List<User>) {
  LazyColumn {
    items(users) { user -> // No key!
      UserListItem(user)
    }
  }
}

@Composable
fun UserListItem(user: User) {
  val expensive = complexCalculation() // Recomputed every render
  Text(user.name)
}
```

**Right**:
```kotlin
@Composable
fun UserList(users: List<User>) {
  LazyColumn {
    items(users, key = { it.id }) { user ->
      UserListItem(user)
    }
  }
}

@Composable
fun UserListItem(user: User) {
  val expensive = remember(user.id) { complexCalculation() }
  Text(user.name)
}
```

---

### Large Images Without Optimization — Severity: HIGH

**What**: Loading full-resolution images. No compression, caching, or resizing. Loading 4MB images for 200px thumbnails.

**Detect**: Large APK/IPA; memory profiler shows image heap; slow image loading; app crashes with image galleries.

**Why Bad**: Memory exhaustion; OOM crashes; battery drain; slow loading; jank when scrolling.

**Fix**: Compress images. Use appropriate resolution. Implement caching. Lazy load. Use libraries like Coil/Glide.

**Wrong**:
```kotlin
@Composable
fun ProductThumbnail(imageUrl: String) {
  Image(
    painter = rememberAsyncImagePainter(imageUrl), // Full resolution download
    contentDescription = null,
    modifier = Modifier.size(100.dp)
  )
}

// Manual loading
Picasso.get().load(url).into(imageView)
```

**Right**:
```kotlin
@Composable
fun ProductThumbnail(imageUrl: String) {
  Image(
    painter = rememberAsyncImagePainter(
      ImageRequest.Builder(LocalContext.current)
        .data(imageUrl)
        .size(Size(100, 100)) // Request only needed size
        .build()
    ),
    contentDescription = null,
    modifier = Modifier.size(100.dp)
  )
}

// With Coil
Coil.imageLoader(context).enqueue(
  ImageRequest.Builder(context)
    .data(url)
    .transformations(ScaleTransformation(100, 100))
    .build()
)
```

---

### Synchronous Operations on Main Thread — Severity: CRITICAL

**What**: Database queries, file I/O, or API calls on main thread. Network on main thread. JSON parsing on main thread.

**Detect**: StrictMode warnings; ANR dialogs; "Skipped X frames" in Logcat; UI freezes.

**Why Bad**: ANR crashes; jank; unresponsive UI; battery drain; app killed by system.

**Fix**: Move work to background threads. Use coroutines, Flow, RxJava, or threading APIs.

**Wrong**:
```kotlin
fun loadUsers() {
  val users = database.userDao().getAllUsers() // BLOCKS!
  updateUI(users)
}

class UserActivity : AppCompatActivity() {
  override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    val data = Gson().fromJson(largeJsonString, MyType::class.java) // BLOCKS!
  }
}
```

**Right**:
```kotlin
fun loadUsers() = viewModelScope.launch {
  val users = withContext(Dispatchers.IO) {
    database.userDao().getAllUsers()
  }
  updateUI(users)
}

class UserActivity : AppCompatActivity() {
  override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    lifecycleScope.launch(Dispatchers.Default) {
      val data = Gson().fromJson(largeJsonString, MyType::class.java)
      withContext(Dispatchers.Main) { updateUI(data) }
    }
  }
}
```

---

### Memory Leaks (Retained References) — Severity: CRITICAL

**What**: Circular references between Activity and ViewModel. Static references to Context. Inner classes holding outer class reference.

**Detect**: LeakCanary warnings; heap dump analysis; app using excess RAM over time.

**Why Bad**: OOM crashes; app force-closes; battery drain; progressive memory exhaustion.

**Fix**: Clear references in onDestroy(). Use weak references for Callbacks. Don't store Context in static.

**Wrong**:
```kotlin
class MyViewModel : ViewModel() {
  private var context: Context = null // Context leak!

  fun init(context: Context) {
    this.context = context // Outlives activity
  }
}

class UserActivity : AppCompatActivity() {
  companion object {
    private var activity: UserActivity? = null // Static reference!
  }

  override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    activity = this
  }
}
```

**Right**:
```kotlin
class MyViewModel(private val context: Context) : ViewModel() {
  // Never store context directly; use as needed
  fun getAppName() = context.getString(R.string.app_name)
}

// Or use platform-independent approach
class MyViewModel(private val resourceProvider: ResourceProvider) : ViewModel()

class UserActivity : AppCompatActivity() {
  // No static reference
}
```

---

### N+1 Queries — Severity: HIGH

**What**: Load parent, then loop loading children. `SELECT user; for each user { SELECT orders; }` instead of JOIN.

**Detect**: Database profiler shows excessive queries; app slow with many items; network waterfall with repeated calls.

**Why Bad**: Exponential slowdown; excessive database load; poor user experience; battery drain.

**Fix**: Use JOIN queries. Batch load. Eager load relationships. Use proper ORM configuration.

**Wrong**:
```kotlin
suspend fun getUsersWithOrders(): List<UserWithOrders> {
  val users = database.userDao().getAllUsers() // N queries
  val result = users.map { user ->
    val orders = database.orderDao().getOrdersForUser(user.id) // N more
    UserWithOrders(user, orders)
  }
  return result
}
```

**Right**:
```kotlin
suspend fun getUsersWithOrders(): List<UserWithOrders> {
  return database.userOrderDao().getUsersWithOrders() // 1 JOIN query
}

@Dao
interface UserOrderDao {
  @Query("""
    SELECT users.*, orders.*
    FROM users
    LEFT JOIN orders ON users.id = orders.user_id
  """)
  suspend fun getUsersWithOrders(): List<UserWithOrders>
}
```

---

### Unbounded List Rendering (No Virtualization) — Severity: HIGH

**What**: Render 10,000 list items at once. No pagination or windowing. Create Views for items not visible.

**Detect**: App freezes on large lists; memory explodes with data; scroll is janky.

**Why Bad**: Memory explosion; jank; OOM crashes; battery drain; interaction becomes impossible.

**Fix**: Use RecyclerView, LazyColumn, or paginated lists. Implement virtualization. Load on-demand.

**Wrong**:
```kotlin
@Composable
fun HugeList(items: List<Item>) {
  Column {
    items.forEach { item -> // Renders ALL at once
      Text(item.name)
    }
  }
}

// Android
LinearLayout {
  for (item in items) {
    addView(createItemView(item)) // All items, always
  }
}
```

**Right**:
```kotlin
@Composable
fun HugeList(items: List<Item>) {
  LazyColumn { // Only renders visible items
    items(items, key = { it.id }) { item ->
      Text(item.name)
    }
  }
}

// Android - RecyclerView with pagination
class ItemAdapter : PagingDataAdapter<Item, ItemViewHolder>(ItemDiffCallback()) {
  override fun onBindViewHolder(holder: ItemViewHolder, position: Int) {
    holder.bind(getItem(position))
  }
}
```

---

### Excessive Logging in Production — Severity: MEDIUM

**What**: Logging every network call, every state change, every user action to disk.

**Detect**: Logcat flooded; large log files; disk fills up; battery drain from write amplification.

**Why Bad**: Battery drain; storage exhaustion; performance impact; crash on write failure.

**Fix**: Conditional logging. Remove verbose logs in release. Use proper log levels.

**Wrong**:
```kotlin
fun processPayment(amount: Double) {
  Log.d("TAG", "Processing payment for $amount") // Every call
  val result = api.charge(amount)
  Log.d("TAG", "Payment result: $result") // Every response
  for (item in items) {
    Log.d("TAG", "Processing item ${item.name}") // N times
  }
}
```

**Right**:
```kotlin
fun processPayment(amount: Double) {
  if (BuildConfig.DEBUG) {
    Log.d("TAG", "Processing payment for $amount")
  }
  val result = api.charge(amount)
  if (result.isError) {
    Log.e("TAG", "Payment failed: ${result.error}")
  }
}
```

---

### Cold Start Bloat — Severity: MEDIUM

**What**: App initialization loads entire database, caches, and configurations at startup. No lazy initialization.

**Detect**: First launch takes 10+ seconds; splash screen lingering; app startup profiler shows heavy load.

**Why Bad**: Poor first impression; ANR on slow devices; user leaves app; battery drain on startup.

**Fix**: Defer initialization. Lazy load. Prioritize user-facing features. Background non-critical init.

**Wrong**:
```kotlin
class App : Application() {
  override fun onCreate() {
    super.onCreate()
    // Load everything at startup
    database = Room.databaseBuilder(this, AppDatabase::class.java, "db").build()
    database.loadAllUsers() // BLOCKS
    database.loadAllProducts() // BLOCKS
    cache.preloadImages() // BLOCKS
  }
}
```

**Right**:
```kotlin
class App : Application() {
  val database: AppDatabase by lazy {
    Room.databaseBuilder(this, AppDatabase::class.java, "db").build()
  }

  override fun onCreate() {
    super.onCreate()
    // Defer non-critical init
    backgroundScope.launch {
      cache.preloadImages()
    }
  }
}
```

---

### Animation on Layout Thread — Severity: HIGH

**What**: Animate layout changes. Measure/layout during animation. Animating many properties simultaneously.

**Detect**: Jank during animations; dropped frames; animation profiler shows GPU rendering > 16ms.

**Why Bad**: Jank; dropped frames; choppy animations; poor perceived performance.

**Fix**: Use GPU-accelerated properties only (transform, opacity). Use proper animation APIs.

**Wrong**:
```kotlin
animate {
  animateTo(Rect(width = newWidth, height = newHeight)) // Layout changes during animation!
}

ObjectAnimator.ofInt(view, "width", 100, 500).start() // Not GPU-accelerated
```

**Right**:
```kotlin
animate {
  animateTo(Offset(x = newX), scaleX = newScale) // Transform/scale only
}

ObjectAnimator.ofFloat(view, "scaleX", 1f, 2f).start() // GPU-accelerated
ObjectAnimator.ofFloat(view, "alpha", 0.5f, 1f).start() // GPU-accelerated
```

---

### Bundle Size Explosion — Severity: MEDIUM

**What**: App includes unused dependencies, large libraries for single functions, debug symbols in release build.

**Detect**: APK > 50MB; IPA > 100MB; unused dependencies in Gradle.

**Why Bad**: Slow install; Play Store warnings; rejection; user abandonment before install.

**Fix**: Remove unused dependencies. Use library subset (androidx vs com.google.android). Enable R8 shrinking.

**Wrong**:
```gradle
dependencies {
  implementation 'com.google.android:google-android-material:1.0' // Whole library
  implementation 'junit:junit:4.13' // Test dependency in production
  implementation 'commons-lang:commons-lang:2.6' // Obsolete
}
```

**Right**:
```gradle
dependencies {
  implementation 'androidx.material:material:1.2.1'
  testImplementation 'junit:junit:4.13' // Test only
}

android {
  buildTypes {
    release {
      minifyEnabled true
      shrinkResources true
      proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
    }
  }
}
```

---

## SECURITY ANTI-PATTERNS

### Hardcoded Secrets/API Keys — Severity: CRITICAL

**What**: API keys, tokens, and passwords in source code. Hardcoded in BuildConfig or string resources.

**Detect**: `val API_KEY = "sk_live_..."` in code; git history with secrets; strings.xml containing keys.

**Why Bad**: Exposed in APK/IPA; visible in decompiled code; accessible to anyone with app; account compromise.

**Fix**: Use build configuration. Store in gradle.properties (not in repo). Use secure backend endpoints.

**Wrong**:
```kotlin
const val API_KEY = "sk_live_4eC39HqLyjWDarht"
const val STRIPE_KEY = "pk_test_..."

val client = HttpClient {
  defaultRequest {
    header("Authorization", "Bearer " + API_KEY)
  }
}
```

**Right**:
```kotlin
// gradle.properties (git-ignored)
STRIPE_API_KEY=sk_live_...

// build.gradle
android {
  buildTypes {
    release {
      buildConfigField "String", "STRIPE_API_KEY", "\"${STRIPE_API_KEY}\""
    }
  }
}

// Use via BuildConfig
val client = HttpClient {
  defaultRequest {
    header("Authorization", "Bearer " + BuildConfig.STRIPE_API_KEY)
  }
}
```

---

### Storing Tokens in Plain SharedPreferences/UserDefaults — Severity: CRITICAL

**What**: Auth tokens stored in SharedPreferences or UserDefaults unencrypted. Anyone reading app data can steal tokens.

**Detect**: SharedPreferences containing "token", "auth", "password"; tokens readable via adb logcat.

**Why Bad**: Tokens stolen if device compromised; account hijacking; complete access to user data.

**Fix**: Use EncryptedSharedPreferences (Android) or Keychain (iOS). Never plaintext storage.

**Wrong**:
```kotlin
val prefs = context.getSharedPreferences("auth", Context.MODE_PRIVATE)
prefs.edit().putString("authToken", token).apply() // Plaintext!

// iOS
UserDefaults.standard.setValue(token, forKey: "authToken") // Plaintext!
```

**Right**:
```kotlin
val encryptedPrefs = EncryptedSharedPreferences.create(
  context,
  "secret_shared_prefs",
  MasterKey.Builder(context).setKeyScheme(MasterKey.KeyScheme.AES256_GCM).build(),
  EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
  EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
)
encryptedPrefs.edit().putString("authToken", token).apply() // Encrypted

// iOS
try {
  let query: [String: Any] = [
    kSecClass as String: kSecClassGenericPassword,
    kSecAttrAccount as String: "authToken",
    kSecValueData as String: token.data(using: .utf8)!
  ]
  SecItemAdd(query as CFDictionary, nil)
} catch { /* handle error */ }
```

---

### Missing Certificate Pinning — Severity: HIGH

**What**: App trusts any valid certificate. Man-in-the-middle possible on compromised networks (airports, etc).

**Detect**: No OkHttp Interceptor for pinning; standard HttpClient without pin verification.

**Why Bad**: MITM attacks possible; data interception; credentials stolen; malware injection.

**Fix**: Implement certificate pinning. Pin domain certificates or public key.

**Wrong**:
```kotlin
val client = OkHttpClient() // Standard, no pinning
```

**Right**:
```kotlin
val certificatePinner = CertificatePinner.Builder()
  .add("api.example.com", "sha256/..." )
  .add("api.example.com", "sha256/..." )
  .build()

val client = OkHttpClient.Builder()
  .certificatePinner(certificatePinner)
  .build()
```

---

### Logging Sensitive Data — Severity: HIGH

**What**: Logging user emails, phone numbers, payment info, or auth tokens in Logcat.

**Detect**: Logcat containing PII; logs with "email", "phone", "card"; production app logging credentials.

**Why Bad**: Logcat accessible via adb; logs leaked in crash reports; PII exposed; regulatory violations.

**Fix**: Never log PII. Hash or redact sensitive data. Disable logging in release.

**Wrong**:
```kotlin
Log.d("AUTH", "User logged in: ${user.email}") // PII!
Log.d("PAYMENT", "Card: ${cardNumber}") // PII!
Log.e("ERROR", "Auth failed with token: ${authToken}") // Credential!
```

**Right**:
```kotlin
if (BuildConfig.DEBUG) {
  Log.d("AUTH", "User logged in: ${user.email.substring(0, 3)}***")
}
Log.d("PAYMENT", "Payment processed for card ending in ${cardNumber.takeLast(4)}")
Log.e("ERROR", "Auth failed") // No credentials
```

---

### SQL Injection in Local DB Queries — Severity: HIGH

**What**: Concatenating user input into SQL strings. Even for local database.

**Detect**: SQL strings with + operator; user input in query builders; raw SQL queries.

**Why Bad**: Malicious data can modify queries; delete data; leak information; corrupt database.

**Fix**: Use parameterized queries. Room with placeholders. Prepared statements.

**Wrong**:
```kotlin
val userId = userInput
val query = "SELECT * FROM users WHERE id = '$userId'" // Injection!
database.rawQuery(query, null)
```

**Right**:
```kotlin
val userId = userInput
val query = "SELECT * FROM users WHERE id = ?"
database.rawQuery(query, arrayOf(userId)) // Safe

// Or Room
@Query("SELECT * FROM users WHERE id = :userId")
suspend fun getUserById(userId: String): User
```

---

### Insecure WebView Configuration — Severity: CRITICAL

**What**: WebView with JavaScript enabled, file:// URLs allowed, mixed content allowed, or debug enabled in release.

**Detect**: webView.settings.javaScriptEnabled = true; allowFileAccess; webviewDebuggingEnabled; mixed HTTP/HTTPS.

**Why Bad**: JavaScript can access Java methods; file access vulnerability; XSS attacks; app compromise.

**Fix**: Disable unnecessary features. Sanitize content. Use HTTPS only. Disable debug.

**Wrong**:
```kotlin
webView.settings.javaScriptEnabled = true
webView.settings.allowFileAccess = true
webView.settings.mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW
WebView.setWebContentsDebuggingEnabled(true) // Debug enabled in release!

webView.addJavascriptInterface(object { // Exposed to JS!
  @JavascriptInterface
  fun getAuthToken() = tokenStorage.getToken()
}, "Android")
```

**Right**:
```kotlin
webView.settings.apply {
  javaScriptEnabled = true // Only if needed
  allowFileAccess = false
  allowContentAccess = false
  mixedContentMode = WebSettings.MIXED_CONTENT_NEVER_ALLOW
}
WebView.setWebContentsDebuggingEnabled(BuildConfig.DEBUG) // Only in debug

// Minimize surface
interface WebInterface {
  @JavascriptInterface
  fun onPageReady() // Safe, no data exposure
}
webView.addJavascriptInterface(WebInterface(), "WebBridge")
```

---

### Missing Input Validation — Severity: HIGH

**What**: Accepting user input without checking format, length, or content. Storing any string in database.

**Detect**: No regex validation; accepting 10MB strings; storing raw HTML; no length checks.

**Why Bad**: XSS in displayed content; DoS from large payloads; SQL injection; app crashes; data corruption.

**Fix**: Validate all input. Whitelist valid formats. Enforce limits. Sanitize before display.

**Wrong**:
```kotlin
fun createUser(name: String, email: String, password: String) {
  repository.saveUser(User(name, email, password)) // No validation!
}

// Display user input
Text(userComment) // XSS if from untrusted source
```

**Right**:
```kotlin
fun createUser(name: String, email: String, password: String): Result<Unit> = runCatching {
  require(name.isNotBlank() && name.length < 100) { "Invalid name" }
  require(email.matches(Regex("^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}$"))) { "Invalid email" }
  require(password.length >= 8) { "Password too short" }
  repository.saveUser(User(name, email, password))
}

// Sanitize before display
val sanitized = HtmlCompat.fromHtml(userComment, HtmlCompat.FROM_HTML_MODE_LEGACY)
Text(sanitized)
```

---

### Screenshot of Sensitive Data Allowed — Severity: MEDIUM

**What**: User can take screenshots of sensitive screens (payment, account details) without warning.

**Detect**: No FLAG_SECURE; screenshots work on sensitive screens; backup allowed on secure data.

**Why Bad**: Screenshots in device storage; cloud backup of credentials; shared devices leak data.

**Fix**: Flag sensitive windows as secure. Disable backup. Warn user on sensitive screens.

**Wrong**:
```kotlin
class PaymentActivity : AppCompatActivity() {
  override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    // No FLAG_SECURE - screenshots allowed
  }
}
```

**Right**:
```kotlin
class PaymentActivity : AppCompatActivity() {
  override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    window.setFlags(WindowManager.LayoutParams.FLAG_SECURE, WindowManager.LayoutParams.FLAG_SECURE)
  }
}

// AndroidManifest.xml
<application android:allowBackup="false">
```

---

## UX ANTI-PATTERNS

### Splash Screen as Loading Screen — Severity: MEDIUM

**What**: Splash screen shown while loading critical data. App can't do anything until data loads. No preloading.

**Detect**: Blank app after splash; long splash duration; splash shown on every cold start.

**Why Bad**: Perceived slowness; user abandonment; poor first impression; blocking entry.

**Fix**: Preload essential data before launch. Show splash while preparing, not loading. Use background sync.

**Wrong**:
```kotlin
class SplashActivity : AppCompatActivity() {
  override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    setContentView(R.layout.splash)

    Thread.sleep(2000) // Artificial delay
    loadUsersFromDatabase() // Blocking
    navigateToHome()
  }
}
```

**Right**:
```kotlin
class App : Application() {
  override fun onCreate() {
    super.onCreate()
    // Preload in background
    backgroundScope.launch(Dispatchers.IO) {
      preloadEssentialData()
    }
  }
}

class LauncherActivity : AppCompatActivity() {
  override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    // Navigate immediately; data loads in background
    startActivity(Intent(this, MainActivity::class.java))
    finish()
  }
}
```

---

### Blocking UI for Network Calls — Severity: CRITICAL

**What**: Button disabled during request. User waits with no feedback. No cancellation option.

**Detect**: Unresponsive UI during network calls; no loading indicator; button stuck.

**Why Bad**: Appears frozen; user hits back; lost requests; frustration.

**Fix**: Show loading state. Keep UI responsive. Allow cancellation. Queue requests if needed.

**Wrong**:
```kotlin
fun onSaveClick() {
  saveButton.isEnabled = false // Frozen!
  viewModel.saveUser(user)
}
```

**Right**:
```kotlin
fun onSaveClick() {
  viewModel.saveUser(user)
}

// In UI
val isSaving by viewModel.isSaving.collectAsState()
Button(
  onClick = { onSaveClick() },
  enabled = !isSaving
) {
  if (isSaving) {
    CircularProgressIndicator(modifier = Modifier.size(16.dp))
  } else {
    Text("Save")
  }
}
```

---

### No Empty/Error/Loading States — Severity: HIGH

**What**: Only showing content state. Blank screen when empty. Crash errors shown to user. No loading indicator.

**Detect**: App shows nothing when list is empty; error dialogs with stack traces; silent loading.

**Why Bad**: Confusing UX; users don't know what happened; errors incomprehensible; appears broken.

**Fix**: Show explicit states. Empty message. User-friendly errors. Loading indicator.

**Wrong**:
```kotlin
@Composable
fun UserList(viewModel: UserListViewModel) {
  val users by viewModel.users.collectAsState()
  LazyColumn {
    items(users) { UserListItem(it) } // Blank if empty!
  }
}
```

**Right**:
```kotlin
@Composable
fun UserList(viewModel: UserListViewModel) {
  val uiState by viewModel.uiState.collectAsState()

  when (uiState) {
    is UiState.Loading -> LoadingSpinner()
    is UiState.Empty -> EmptyPlaceholder("No users found")
    is UiState.Content -> LazyColumn {
      items(uiState.users) { UserListItem(it) }
    }
    is UiState.Error -> ErrorMessage(
      message = uiState.error.userMessage,
      onRetry = { viewModel.reload() }
    )
  }
}
```

---

### Breaking Platform Back Navigation — Severity: MEDIUM

**What**: Custom back button. Ignoring system back. Breaking Android back stack.

**Detect**: App doesn't respond to back gesture; custom back button; navigation not added to back stack.

**Why Bad**: Violates platform conventions; user frustration; app appears broken.

**Fix**: Use Navigation component. Handle onBackPressedDispatcher. Respect platform conventions.

**Wrong**:
```kotlin
class MyFragment : Fragment() {
  fun onCustomBackClick() {
    parentFragmentManager.popBackStack() // Manual!
  }
}
```

**Right**:
```kotlin
class MyFragment : Fragment() {
  override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
    requireActivity().onBackPressedDispatcher.addCallback(viewLifecycleOwner) {
      if (hasUnsavedChanges()) {
        showConfirmDialog()
      } else {
        isEnabled = false
        requireActivity().onBackPressed()
      }
    }
  }
}

// Or use Navigation
navController.navigate(R.id.action_next)
// Back is automatic
```

---

### Custom Gestures Conflicting with System Gestures — Severity: MEDIUM

**What**: App intercepts system gestures (back swipe, bottom navigation). Swipe-to-go-back intercepted by ViewPager.

**Detect**: Back gesture doesn't work; bottom swipe triggers wrong action; conflicts in gesture detector.

**Why Bad**: Breaks expected behavior; user confusion; accessibility issues.

**Fix**: Use platform gestures. Don't intercept system gestures. Proper gesture hierarchy.

**Wrong**:
```kotlin
val gestureDetector = GestureDetector(context, object : GestureDetector.SimpleOnGestureListener() {
  override fun onFling(e1: MotionEvent, e2: MotionEvent, vx: Float, vy: Float): Boolean {
    if (e1.x - e2.x > 100) { // Left swipe
      goBack() // Intercepts system back!
    }
    return true
  }
})
```

**Right**:
```kotlin
// Let system handle gestures
requireActivity().onBackPressedDispatcher.addCallback { goBack() }

// Or swipe with proper interceptor
PagerSnapHelper().attachToRecyclerView(recyclerView)
```

---

### Aggressive Permission Requests on First Launch — Severity: MEDIUM

**What**: App asks for location, contacts, camera on first launch. Multiple permission dialogs at once.

**Detect**: Permission dialogs before showing app; multiple dialogs in sequence; no explanation why.

**Why Bad**: User denies permissions reflexively; reduced adoption; bad reviews.

**Fix**: Request permissions when needed. Show context first. Explain why.

**Wrong**:
```kotlin
override fun onCreate(savedInstanceState: Bundle?) {
  super.onCreate(savedInstanceState)
  requestPermissions(arrayOf(
    Manifest.permission.ACCESS_FINE_LOCATION,
    Manifest.permission.ACCESS_COARSE_LOCATION,
    Manifest.permission.CAMERA,
    Manifest.permission.READ_CONTACTS
  ), 1) // All at once on launch!
}
```

**Right**:
```kotlin
// Request when needed
fun onMapScreenShown() {
  if (hasLocationPermission()) {
    showMap()
  } else {
    showPermissionRationale("We need location to show you nearby places")
    requestPermissions(arrayOf(Manifest.permission.ACCESS_FINE_LOCATION), REQUEST_LOCATION)
  }
}
```

---

### No Keyboard Avoidance — Severity: MEDIUM

**What**: EditText hidden behind keyboard. Form fields don't scroll into view. No window adjustment.

**Detect**: EditText unreachable when keyboard open; content goes off-screen; text visible but unreachable.

**Why Bad**: Can't interact with hidden fields; poor UX; frustration.

**Fix**: Set windowSoftInputMode. Use ScrollView. Handle keyboard visibility.

**Wrong**:
```xml
<activity android:windowSoftInputMode="adjustNothing" />
```

**Right**:
```xml
<activity android:windowSoftInputMode="adjustResize|stateHidden" />

<!-- Or in code -->
class FormActivity : AppCompatActivity() {
  override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    window.setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE)
  }
}
```

---

### Modal Overuse — Severity: LOW

**What**: Every action shown in modal. Alert dialogs for confirmations. Nested modals.

**Detect**: Multiple dialogs stacked; modal for simple choice; modal doesn't dismiss.

**Why Bad**: Navigation confusing; gestures blocked; difficult to escape; feels claustrophobic.

**Fix**: Use modals for critical choices only. Show bottom sheets for content. Dialogs for alerts.

**Wrong**:
```kotlin
// Everything is a modal
showModal {
  showModal {
    showModal {
      ChooseOption()
    }
  }
}
```

**Right**:
```kotlin
// Bottom sheet for content
ModalBottomSheet(onDismissRequest = { /* close */ }) {
  OptionList()
}

// Dialog for alerts only
AlertDialog(
  onDismissRequest = { },
  title = { Text("Confirm") },
  text = { Text("Delete item?") }
)
```

---

## TESTING ANTI-PATTERNS

### Testing Implementation Not Behavior — Severity: MEDIUM

**What**: Tests verify internal methods, private variables, or exact call counts. Mock every dependency.

**Detect**: Test imports private methods; mocks injected to verify calls; test breaks on refactoring; testing mocks.

**Why Bad**: Tests brittle; refactoring hard; tests don't catch regressions; false security.

**Fix**: Test observable behavior. Test through public APIs. Mock only boundaries.

**Wrong**:
```kotlin
@Test
fun testUserListViewModel() {
  val mockRepository = mock(UserRepository::class.java)
  val viewModel = UserListViewModel(mockRepository)

  verify(mockRepository).getUsers() // Mocking verification
  assertTrue(viewModel.filterUsers.wasInvoked) // Checking internal method
}
```

**Right**:
```kotlin
@Test
fun testUserListViewModelLoadsUsers() {
  val fakeRepository = FakeUserRepository()
  val viewModel = UserListViewModel(fakeRepository)

  assertEquals(expectedUsers, viewModel.users.value) // Observable behavior
}
```

---

### Flaky UI Tests — Severity: MEDIUM

**What**: UI tests pass/fail randomly. Timing-dependent. No waits for async operations.

**Detect**: Tests pass sometimes; fail on CI; depend on speed; timeouts random.

**Why Bad**: Can't trust test results; CI unreliable; developer frustration.

**Fix**: Use proper waits. ComposeTestRule.waitUntil(). Espresso idling resources.

**Wrong**:
```kotlin
@Test
fun testLoadUsers() {
  composeTestRule.setContent { UserList() }
  Thread.sleep(1000) // Hope it loads!
  composeTestRule.onNodeWithText("User 1").assertExists()
}
```

**Right**:
```kotlin
@Test
fun testLoadUsers() {
  composeTestRule.setContent { UserList(viewModel) }
  composeTestRule.waitUntil(timeoutMillis = 5000) {
    composeTestRule.onNodeWithText("User 1").isDisplayed()
  }
}
```

---

### No Test Isolation — Severity: MEDIUM

**What**: Tests depend on execution order. Shared state between tests. Database not cleaned.

**Detect**: Tests pass individually but fail together; test order matters; shared mutable state.

**Why Bad**: Flaky tests; hard to debug; tests pass locally but fail CI.

**Fix**: Isolate each test. Clean up after. Use setup/teardown.

**Wrong**:
```kotlin
var db: AppDatabase? = null

@Test
fun testCreateUser() {
  if (db == null) db = createDatabase() // Shared!
  db!!.userDao().insert(user)
}

@Test
fun testFetchUser() {
  val user = db!!.userDao().get(userId) // Depends on previous test!
}
```

**Right**:
```kotlin
@get:Rule
val instantExecutorRule = InstantTaskExecutorRule()

@Before
fun setup() {
  db = Room.inMemoryDatabaseBuilder(context, AppDatabase::class.java).build()
}

@After
fun tearDown() {
  db.close()
}

@Test
fun testCreateUser() {
  db.userDao().insert(user)
  val fetched = db.userDao().get(user.id)
  assertEquals(user, fetched)
}
```

---

### Snapshot Tests Without Review — Severity: LOW

**What**: Taking snapshot without reviewing. Committing snapshots with bugs. Updates without inspection.

**Detect**: Large snapshot files; snapshot updates with no review; snapshots of full screens.

**Why Bad**: Snapshots become "expected" bugs; regressions missed; snapshots outdated.

**Fix**: Review snapshots carefully. Update intentionally. Snapshot small units.

---

### Mocking Everything — Severity: MEDIUM

**What**: Mock Repository, mock Database, mock API. Testing mocks not actual code. 100% mocked dependencies.

**Detect**: No real objects in tests; all dependencies mocked; test doesn't use actual code paths.

**Why Bad**: Tests pass but code fails; real bugs not caught; no confidence in code.

**Fix**: Use fakes for boundaries. Real objects for logic. Test actual code paths.

**Wrong**:
```kotlin
@Test
fun testAddToCart() {
  val mockRepository = mock(CartRepository::class.java)
  `when`(mockRepository.addItem(any())).thenReturn(true)

  val viewModel = CartViewModel(mockRepository)
  viewModel.addItem(item)

  verify(mockRepository).addItem(item) // Testing mock not code
}
```

**Right**:
```kotlin
@Test
fun testAddToCart() {
  val fakeRepository = FakeCartRepository() // Real behavior
  val viewModel = CartViewModel(fakeRepository)

  viewModel.addItem(item)

  assertEquals(listOf(item), fakeRepository.items) // Real result
}
```

---

## PLATFORM-SPECIFIC ANTI-PATTERNS

### Ignoring Process Death (Android) — Severity: HIGH

**What**: App assumes process won't be killed. No SavedState. Activity state lost on app backgrounding.

**Detect**: App crashes on resume after backgrounding; back button recreates from scratch; no savedInstanceState.

**Why Bad**: Data loss; poor UX; crashes on resume; perceived app instability.

**Fix**: Use SavedStateHandle. Save/restore state. Implement correct lifecycle.

**Wrong**:
```kotlin
class UserDetailViewModel : ViewModel() {
  var userId: String = "" // Lost on process death!
}

class UserDetailActivity : AppCompatActivity() {
  override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    // Ignoring savedInstanceState
  }
}
```

**Right**:
```kotlin
class UserDetailViewModel(private val savedStateHandle: SavedStateHandle) : ViewModel() {
  val userId: StateFlow<String> =
    savedStateHandle.getStateFlow("userId", "")
}

class UserDetailActivity : AppCompatActivity() {
  private val viewModel: UserDetailViewModel by viewModels()

  override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    if (savedInstanceState != null) {
      viewModel.restore(savedInstanceState)
    }
  }

  override fun onSaveInstanceState(outState: Bundle) {
    viewModel.save(outState)
    super.onSaveInstanceState(outState)
  }
}
```

---

### Not Handling Scene Lifecycle (iOS) — Severity: HIGH

**What**: Ignoring sceneDidEnterBackground, sceneWillEnterForeground. Resources not released on backgrounding. UI not updated on resume.

**Detect**: App doesn't respond to background/foreground; memory not freed on background; data inconsistent after resume.

**Why Bad**: Memory leak; battery drain; stale data; crashes.

**Fix**: Implement SceneDelegate. Handle lifecycle events. Refresh data on foreground.

**Wrong**:
```swift
class SceneDelegate: UIResponder, UIWindowSceneDelegate {
  func sceneDidEnterBackground(_ scene: UIScene) {
    // Not implemented
  }
}
```

**Right**:
```swift
class SceneDelegate: UIResponder, UIWindowSceneDelegate {
  func sceneDidEnterBackground(_ scene: UIScene) {
    networkClient.cancel() // Stop requests
    databaseConnection.close() // Release resources
  }

  func sceneWillEnterForeground(_ scene: UIScene) {
    fetchFreshData() // Refresh on resume
  }
}
```

---

### Ignoring Safe Areas — Severity: MEDIUM

**What**: Layout extends under notch/dynamic island. Content hidden. Views not respecting safe area insets.

**Detect**: Content behind notch; text unreadable near edges; buttons unreachable.

**Why Bad**: Content unreachable; poor UX; looks broken.

**Fix**: Respect safeAreaLayoutGuide. Use safeAreaInsets. Test on device with notch.

**Wrong**:
```swift
view.frame = UIScreen.main.bounds // Ignores safe area
```

**Right**:
```swift
view.frame = view.window?.windowScene?.screen.bounds.inset(by: view.safeAreaInsets) ?? .zero

// Or constraints
NSLayoutConstraint.activate([
  contentView.leadingAnchor.constraint(equalTo: view.safeAreaLayoutGuide.leadingAnchor),
  contentView.trailingAnchor.constraint(equalTo: view.safeAreaLayoutGuide.trailingAnchor),
  contentView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
  contentView.bottomAnchor.constraint(equalTo: view.safeAreaLayoutGuide.bottomAnchor)
])
```

---

### Hardcoded Dimensions — Severity: MEDIUM

**What**: Layout hardcodes pixel values. No scaling for screen sizes. Constants for font sizes.

**Detect**: `frame = CGRect(x: 100, y: 50, width: 200, height: 300)`; no responsive layout.

**Why Bad**: Breaks on tablets; landscape orientation fails; different screens look bad.

**Fix**: Use relative sizing. Proportional spacing. Responsive layouts.

**Wrong**:
```kotlin
Button(modifier = Modifier.size(width = 100.dp, height = 50.dp))

Text(fontSize = 16.sp) // Fixed size
```

**Right**:
```kotlin
Button(modifier = Modifier.fillMaxWidth(fraction = 0.8f).height(50.dp))

Text(fontSize = 4.w) // Responsive to screen width

@Composable
fun ResponsiveLayout() {
  val screenWidth = LocalConfiguration.current.screenWidthDp
  val columnCount = if (screenWidth > 600) 3 else 1

  LazyVerticalGrid(columns = GridCells.Fixed(columnCount)) {
    // Responsive grid
  }
}
```

---

### Platform-Specific Code in Shared Modules — Severity: MEDIUM

**What**: Android imports in shared code. iOS APIs in common layer. Kotlin/Swift mixed.

**Detect**: `android.context.Context` in shared module; iOS frameworks in common code.

**Why Bad**: Code can't be reused; shared module depends on platform; breaks architecture.

**Fix**: Abstract platform differences. Use interfaces. Common layer depends on abstractions.

**Wrong**:
```kotlin
// In common module
import android.content.Context

class DataStore(private val context: Context) {
  fun save(data: String) {
    context.getSharedPreferences("app", Context.MODE_PRIVATE).edit().putString("key", data).apply()
  }
}
```

**Right**:
```kotlin
// Common module
interface LocalStorage {
  fun save(key: String, value: String)
  fun load(key: String): String?
}

// Android implementation
class AndroidLocalStorage(private val context: Context) : LocalStorage {
  override fun save(key: String, value: String) {
    context.getSharedPreferences("app", Context.MODE_PRIVATE).edit().putString(key, value).apply()
  }
}

// iOS implementation
class IosLocalStorage : LocalStorage {
  override fun save(key: String, value: String) {
    UserDefaults.standard.set(value, forKey: key)
  }
}

// Common code
class DataRepository(private val storage: LocalStorage) {
  fun saveUser(user: User) = storage.save("user", user.toJson())
}
```

---

### Not Respecting Dynamic Type/Font Scaling (iOS) — Severity: MEDIUM

**What**: Fixed font sizes. Not respecting user's text size preference (iOS Dynamic Type).

**Detect**: Text doesn't scale with system settings; small text unreadable for accessibility.

**Why Bad**: Accessibility issue; violates iOS guidelines; excludes users with vision impairment.

**Fix**: Use Dynamic Type. Scale fonts with system setting. Use UIFont.preferredFont().

**Wrong**:
```swift
label.font = UIFont.systemFont(ofSize: 16) // Fixed
```

**Right**:
```swift
label.font = UIFont.preferredFont(forTextStyle: .body) // Respects Dynamic Type
label.adjustsFontForContentSizeCategory = true // Update when setting changes

// Compose equivalent
Text("Content", style = LocalTextStyle.current.copy(fontSize = 16.sp.scaledSp))
```

---

This comprehensive reference covers the most critical and common anti-patterns across all major areas of mobile development. Use this as a checklist during code review and architecture planning.
