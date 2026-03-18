# Android Native Development - Comprehensive Kotlin Reference

## Table of Contents

- [1. Kotlin Modern Features](#1-kotlin-modern-features)
- [2. Jetpack Compose](#2-jetpack-compose)
- [3. Navigation](#3-navigation)
- [4. State Management](#4-state-management)
- [5. Data Layer](#5-data-layer)
- [6. Networking](#6-networking)
- [7. Dependency Injection](#7-dependency-injection)
- [8. Architecture Patterns](#8-architecture-patterns)
- [9. Performance Optimization](#9-performance-optimization)
- [10. Testing](#10-testing)
- [11. Animations](#11-animations)
- [12. Push Notifications](#12-push-notifications)
- [13. Background Tasks](#13-background-tasks)
- [14. Material Design 3](#14-material-design-3)
- [15. Distribution & Gradle](#15-distribution--gradle)

## 1. Kotlin Modern Features

### Coroutines & Flow
```kotlin
// Coroutines for async operations
class UserRepository {
    private val coroutineScope = CoroutineScope(Dispatchers.Main + Job())

    suspend fun fetchUser(id: String): User = withContext(Dispatchers.IO) {
        apiService.getUser(id)
    }

    // Flow for reactive streams
    fun getUserUpdates(): Flow<User> = flow {
        while (currentCoroutineContext().isActive) {
            val user = apiService.getUser(userId)
            emit(user)
            delay(30000) // Refresh every 30 seconds
        }
    }.catch { e ->
        Log.e("UserRepo", "Error fetching updates", e)
    }.flowOn(Dispatchers.IO)
}

// SharedFlow for events
class EventBus {
    private val _events = MutableSharedFlow<AppEvent>()
    val events: SharedFlow<AppEvent> = _events.asSharedFlow()

    suspend fun publishEvent(event: AppEvent) {
        _events.emit(event)
    }
}
```

### Sealed Classes & Data Classes
```kotlin
// Sealed classes for type-safe state management
sealed class AuthState {
    object Loading : AuthState()
    data class Success(val user: User) : AuthState()
    data class Error(val exception: Exception) : AuthState()
}

// Data classes with destructuring
data class User(val id: String, val name: String, val email: String) {
    val displayName: String get() = name.uppercase()
}

// Extension functions
fun <T> Flow<T>.throttleFirst(periodMillis: Long): Flow<T> = flow {
    var lastEmissionTime = 0L
    collect { value ->
        val currentTime = System.currentTimeMillis()
        if (currentTime - lastEmissionTime >= periodMillis) {
            emit(value)
            lastEmissionTime = currentTime
        }
    }
}

// DSL for building requests
fun buildApiRequest(init: RequestBuilder.() -> Unit): Request {
    return RequestBuilder().apply(init).build()
}

class RequestBuilder {
    var url: String = ""
    var method: String = "GET"
    val headers = mutableMapOf<String, String>()

    fun header(key: String, value: String) {
        headers[key] = value
    }

    fun build() = Request(url, method, headers)
}
```

## 2. Jetpack Compose

### Composables & Recomposition
```kotlin
@Composable
fun UserListScreen(viewModel: UserViewModel = hiltViewModel()) {
    val users by viewModel.users.collectAsState(initial = emptyList())
    val isLoading by viewModel.isLoading.collectAsState(initial = false)

    LaunchedEffect(Unit) {
        viewModel.loadUsers()
    }

    if (isLoading) {
        CircularProgressIndicator()
    } else {
        LazyColumn {
            items(users, key = { it.id }) { user ->
                UserListItem(user = user, modifier = Modifier.fillMaxWidth())
            }
        }
    }
}

// State hoisting
@Composable
fun UserListItem(user: User, modifier: Modifier = Modifier) {
    var isExpanded by remember { mutableStateOf(false) }

    Column(modifier = modifier.clickable { isExpanded = !isExpanded }) {
        Text(user.name, style = MaterialTheme.typography.titleMedium)
        if (isExpanded) {
            Text(user.email, style = MaterialTheme.typography.bodySmall)
        }
    }
}

// CompositionLocal for theme
val LocalAppTheme = compositionLocalOf { AppTheme.Light }

@Composable
fun ThemedContent() {
    val theme = LocalAppTheme.current
    CompositionLocalProvider(LocalAppTheme provides AppTheme.Dark) {
        // Dark theme applied to children
    }
}

// Side effects
@Composable
fun LocationTracker(onLocationUpdate: (Location) -> Unit) {
    val context = LocalContext.current

    DisposableEffect(Unit) {
        val locationListener = LocationListener { location ->
            onLocationUpdate(location)
        }
        locationManager.requestLocationUpdates(locationListener)

        onDispose {
            locationManager.removeUpdates(locationListener)
        }
    }
}

@Composable
fun AnalyticsScreen(screenName: String) {
    SideEffect {
        Analytics.logScreenView(screenName)
    }
}
```

## 3. Navigation

### Navigation Compose with Type-Safe Args
```kotlin
// Sealed routes
sealed class Route {
    object UserList : Route()
    data class UserDetail(val userId: String) : Route()
    object Settings : Route()
}

// Navigation setup
@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(navController = navController, startDestination = "user_list") {
        composable(route = "user_list") {
            UserListScreen(
                onUserSelected = { userId ->
                    navController.navigate("user_detail/$userId")
                }
            )
        }

        composable(
            route = "user_detail/{userId}",
            arguments = listOf(navArgument("userId") { type = NavType.StringType })
        ) { backStackEntry ->
            val userId = backStackEntry.arguments?.getString("userId") ?: ""
            UserDetailScreen(userId = userId)
        }

        composable(route = "settings") {
            SettingsScreen()
        }
    }
}

// Type-safe navigation with Kotlin serialization
@Serializable
data class UserDetailRoute(val userId: String)

@Composable
fun TypeSafeNavigation() {
    val navController = rememberNavController()

    NavHost(navController = navController, startDestination = UserListRoute) {
        composable<UserListRoute> {
            UserListScreen(onUserSelected = { userId ->
                navController.navigate(UserDetailRoute(userId))
            })
        }

        composable<UserDetailRoute> { backStackEntry ->
            val route = backStackEntry.toRoute<UserDetailRoute>()
            UserDetailScreen(userId = route.userId)
        }
    }
}
```

## 4. State Management

### ViewModel + StateFlow
```kotlin
@HiltViewModel
class UserViewModel @Inject constructor(
    private val userRepository: UserRepository,
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {

    private val _users = MutableStateFlow<List<User>>(emptyList())
    val users: StateFlow<List<User>> = _users.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    private val _error = MutableSharedFlow<String>()
    val error: SharedFlow<String> = _error.asSharedFlow()

    // Restored from savedStateHandle
    private val _selectedUserId = MutableStateFlow(
        savedStateHandle.get<String>("selectedUserId") ?: ""
    )
    val selectedUserId: StateFlow<String> = _selectedUserId.asStateFlow()

    fun loadUsers() {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                val users = userRepository.fetchAllUsers()
                _users.value = users
            } catch (e: Exception) {
                _error.emit(e.message ?: "Unknown error")
            } finally {
                _isLoading.value = false
            }
        }
    }

    fun selectUser(userId: String) {
        _selectedUserId.value = userId
        savedStateHandle["selectedUserId"] = userId
    }
}

// Composable state with remember
@Composable
fun SearchableUserList() {
    var searchQuery by remember { mutableStateOf("") }
    var results by rememberSaveable { mutableStateOf<List<User>>(emptyList()) }

    Column {
        TextField(
            value = searchQuery,
            onValueChange = { searchQuery = it },
            label = { Text("Search") }
        )

        LaunchedEffect(searchQuery) {
            if (searchQuery.isNotEmpty()) {
                results = searchUsers(searchQuery)
            }
        }

        LazyColumn {
            items(results) { user ->
                UserListItem(user)
            }
        }
    }
}
```

## 5. Data Layer

### Room Database
```kotlin
// Entity with primary key
@Entity(tableName = "users")
data class UserEntity(
    @PrimaryKey val id: String,
    val name: String,
    val email: String,
    @ColumnInfo(name = "created_at") val createdAt: Long
)

// DAO with queries
@Dao
interface UserDao {
    @Query("SELECT * FROM users ORDER BY created_at DESC")
    fun getAllUsers(): Flow<List<UserEntity>>

    @Query("SELECT * FROM users WHERE id = :userId")
    suspend fun getUserById(userId: String): UserEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUsers(users: List<UserEntity>)

    @Delete
    suspend fun deleteUser(user: UserEntity)

    @Transaction
    @Query("SELECT * FROM users WHERE id IN (:userIds)")
    suspend fun getUsersWithPosts(userIds: List<String>): List<UserWithPosts>
}

// Database with migrations
@Database(
    entities = [UserEntity::class, PostEntity::class],
    version = 2,
    exportSchema = true
)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
    abstract fun postDao(): PostDao

    companion object {
        val MIGRATION_1_2 = object : Migration(1, 2) {
            override fun migrate(database: SupportSQLiteDatabase) {
                database.execSQL(
                    "ALTER TABLE users ADD COLUMN last_updated INTEGER NOT NULL DEFAULT 0"
                )
            }
        }

        fun getInstance(context: Context): AppDatabase {
            return Room.databaseBuilder(
                context.applicationContext,
                AppDatabase::class.java,
                "app_database"
            )
                .addMigrations(MIGRATION_1_2)
                .build()
        }
    }
}

// DataStore for preferences
val Context.dataStore: DataStore<Preferences> by preferencesDataStore(
    name = "app_preferences"
)

class PreferencesRepository(private val context: Context) {
    companion object {
        val DARK_MODE = booleanPreferencesKey("dark_mode")
        val USER_ID = stringPreferencesKey("user_id")
    }

    val darkModeFlow: Flow<Boolean> = context.dataStore.data
        .map { preferences -> preferences[DARK_MODE] ?: false }
        .catch { emit(false) }

    suspend fun setDarkMode(enabled: Boolean) {
        context.dataStore.edit { preferences ->
            preferences[DARK_MODE] = enabled
        }
    }
}
```

## 6. Networking

### Retrofit + OkHttp
```kotlin
// API Service interface
interface ApiService {
    @GET("users/{id}")
    suspend fun getUser(@Path("id") id: String): User

    @GET("users")
    suspend fun listUsers(@Query("page") page: Int): List<User>

    @POST("users")
    @Headers("Content-Type: application/json")
    suspend fun createUser(@Body user: UserRequest): User

    @Multipart
    @POST("upload")
    suspend fun uploadFile(@Part file: MultipartBody.Part): UploadResponse
}

// OkHttp configuration
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideOkHttp(): OkHttpClient {
        return OkHttpClient.Builder()
            .addInterceptor { chain ->
                val originalRequest = chain.request()
                val requestBuilder = originalRequest.newBuilder()
                    .addHeader("Authorization", "Bearer ${getToken()}")

                chain.proceed(requestBuilder.build())
            }
            .addNetworkInterceptor(
                HttpLoggingInterceptor().apply {
                    level = HttpLoggingInterceptor.Level.BODY
                }
            )
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .build()
    }

    @Provides
    @Singleton
    fun provideRetrofit(okHttpClient: OkHttpClient): Retrofit {
        return Retrofit.Builder()
            .baseUrl("https://api.example.com/")
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    @Provides
    @Singleton
    fun provideApiService(retrofit: Retrofit): ApiService {
        return retrofit.create(ApiService::class.java)
    }
}

// Ktor Client alternative
@Module
@InstallIn(SingletonComponent::class)
object KtorModule {

    @Provides
    @Singleton
    fun provideHttpClient(): HttpClient {
        return HttpClient {
            install(ContentNegotiation) {
                json(Json { ignoreUnknownKeys = true })
            }
            install(HttpTimeout) {
                requestTimeoutMillis = 30000
            }
            install(Logging) {
                level = LogLevel.BODY
            }
        }
    }
}
```

## 7. Dependency Injection

### Hilt Setup
```kotlin
// Application class
@HiltAndroidApp
class MyApplication : Application()

// Module for singleton dependencies
@Module
@InstallIn(SingletonComponent::class)
object AppModule {

    @Provides
    @Singleton
    fun provideUserRepository(
        userDao: UserDao,
        apiService: ApiService
    ): UserRepository {
        return UserRepositoryImpl(userDao, apiService)
    }
}

// Activity injection
@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    private val viewModel: MainViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MainScreen(viewModel = viewModel)
        }
    }
}

// Qualifiers for multiple implementations
@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class LocalDataSource

@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class RemoteDataSource

@Module
@InstallIn(SingletonComponent::class)
object DataSourceModule {

    @Provides
    @Singleton
    @LocalDataSource
    fun provideLocalDataSource(db: AppDatabase): UserDataSource {
        return LocalUserDataSource(db.userDao())
    }

    @Provides
    @Singleton
    @RemoteDataSource
    fun provideRemoteDataSource(api: ApiService): UserDataSource {
        return RemoteUserDataSource(api)
    }
}

// Scoped dependencies
@Module
@InstallIn(ViewModelComponent::class)
object ViewModelModule {

    @Provides
    fun provideUserRepository(
        @LocalDataSource localSource: UserDataSource,
        @RemoteDataSource remoteSource: UserDataSource
    ): UserRepository {
        return UserRepository(localSource, remoteSource)
    }
}
```

### Koin Alternative
```kotlin
// Koin setup
val appModule = module {
    single<ApiService> {
        val client = OkHttpClient.Builder()
            .addInterceptor(HttpLoggingInterceptor())
            .build()

        Retrofit.Builder()
            .baseUrl("https://api.example.com/")
            .client(client)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create()
    }

    single<UserRepository> { UserRepositoryImpl(get()) }

    viewModel { UserViewModel(get()) }
}

// Activity with Koin injection
class MainActivity : AppCompatActivity() {
    private val userViewModel: UserViewModel by viewModel()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
    }
}
```

## 8. Architecture Patterns

### MVVM + Clean Architecture
```kotlin
// Use cases (Domain layer)
class GetUsersUseCase(private val repository: UserRepository) {
    suspend operator fun invoke(): List<User> {
        return repository.fetchAllUsers()
    }
}

// Repository (Data layer)
interface UserRepository {
    suspend fun fetchAllUsers(): List<User>
    fun watchUserUpdates(userId: String): Flow<User>
}

class UserRepositoryImpl(
    private val localDataSource: UserDataSource,
    private val remoteDataSource: UserDataSource
) : UserRepository {

    override suspend fun fetchAllUsers(): List<User> {
        return try {
            val remoteUsers = remoteDataSource.getUsers()
            localDataSource.saveUsers(remoteUsers)
            remoteUsers
        } catch (e: Exception) {
            localDataSource.getUsers()
        }
    }

    override fun watchUserUpdates(userId: String): Flow<User> = flow {
        while (currentCoroutineContext().isActive) {
            try {
                val user = remoteDataSource.getUserById(userId)
                emit(user)
            } catch (e: Exception) {
                // Fallback to local
            }
            delay(30000)
        }
    }
}

// ViewModel (Presentation layer)
@HiltViewModel
class UserViewModel @Inject constructor(
    private val getUsersUseCase: GetUsersUseCase,
    private val userRepository: UserRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<UserUiState>(UserUiState.Loading)
    val uiState: StateFlow<UserUiState> = _uiState.asStateFlow()

    fun loadUsers() {
        viewModelScope.launch {
            try {
                _uiState.value = UserUiState.Loading
                val users = getUsersUseCase()
                _uiState.value = UserUiState.Success(users)
            } catch (e: Exception) {
                _uiState.value = UserUiState.Error(e.message ?: "Unknown error")
            }
        }
    }
}

sealed class UserUiState {
    object Loading : UserUiState()
    data class Success(val users: List<User>) : UserUiState()
    data class Error(val message: String) : UserUiState()
}
```

## 9. Performance Optimization

### Baseline Profiles & R8
```kotlin
// ProGuard rules in proguard-rules.pro
-keep class com.example.myapp.model.** { *; }
-keepclassmembers class * {
    @com.google.gson.annotations.SerializedName <fields>;
}
-dontwarn okhttp3.**
-dontwarn retrofit2.**

// Baseline Profile setup (baselineprofile module)
class BaselineProfileGenerator {
    @get:Rule
    val baselineProfileRule = BaselineProfileRule()

    @Test
    fun startup() = baselineProfileRule.collect {
        pressHome()
        startActivityAndWait(Intent(ACTION_MAIN))
    }
}

// Lazy layouts for performance
@Composable
fun OptimizedList(items: List<Item>) {
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(8.dp)
    ) {
        items(
            items,
            key = { it.id },
            contentType = { "item" }
        ) { item ->
            ItemCard(item, Modifier.fillMaxWidth())
        }
    }
}

// Stability annotations
@Stable
data class UserUiModel(
    val id: String,
    val name: String,
    val email: String
)

@Immutable
data class AppTheme(
    val primaryColor: Color,
    val secondaryColor: Color
)
```

## 10. Testing

### Unit & UI Testing
```kotlin
// JUnit tests with Hilt
@HiltAndroidTest
class UserRepositoryTest {

    @get:Rule
    val hiltRule = HiltAndroidRule(this)

    @Inject
    lateinit var userRepository: UserRepository

    @Before
    fun setup() {
        hiltRule.inject()
    }

    @Test
    fun testFetchUsers() = runTest {
        val users = userRepository.fetchAllUsers()
        assertThat(users).isNotEmpty()
    }
}

// MockK for mocking
class UserViewModelTest {

    private val userRepository: UserRepository = mockk()
    private lateinit var viewModel: UserViewModel

    @Before
    fun setup() {
        viewModel = UserViewModel(userRepository)
    }

    @Test
    fun testLoadUsers() = runTest {
        val mockUsers = listOf(User("1", "John", "john@example.com"))
        coEvery { userRepository.fetchAllUsers() } returns mockUsers

        viewModel.loadUsers()

        val state = viewModel.uiState.value
        assertThat(state).isInstanceOf(UserUiState.Success::class.java)
    }
}

// Compose UI testing
@RunWith(AndroidJUnit4::class)
class UserListScreenTest {

    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun testUserListDisplay() {
        composeTestRule.setContent {
            UserListScreen()
        }

        composeTestRule.onNodeWithText("John Doe").assertIsDisplayed()
        composeTestRule.onNodeWithContentDescription("user_item").assertCountEquals(1)
    }
}

// Espresso testing
class MainActivityTest {

    @get:Rule
    val activityRule = ActivityScenarioRule(MainActivity::class.java)

    @Test
    fun testNavigateToUserDetail() {
        onView(withText("Users")).perform(click())
        onView(withText("John")).perform(click())
        onView(withId(R.id.user_detail_container)).check(matches(isDisplayed()))
    }
}
```

## 11. Animations

### Compose Animations
```kotlin
@Composable
fun AnimatedCard(isExpanded: Boolean) {
    val animatedHeight by animateDpAsState(
        targetValue = if (isExpanded) 300.dp else 100.dp,
        label = "heightAnimation"
    )

    Card(modifier = Modifier.height(animatedHeight)) {
        Text("Animated content")
    }
}

@Composable
fun VisibilityAnimation(isVisible: Boolean) {
    AnimatedVisibility(
        visible = isVisible,
        enter = fadeIn() + slideInVertically(),
        exit = fadeOut() + slideOutVertically()
    ) {
        Text("Appears/disappears with animation")
    }
}

@Composable
fun ContentSwitcher(targetState: ContentState) {
    AnimatedContent(
        targetState = targetState,
        transitionSpec = {
            fadeIn() with fadeOut()
        },
        label = "contentAnimation"
    ) { state ->
        when (state) {
            is ContentState.Loading -> CircularProgressIndicator()
            is ContentState.Success -> Text(state.data)
        }
    }
}

// MotionLayout for complex animations
@Composable
fun MotionLayoutExample() {
    MotionLayout(
        motionScene = MotionSceneContent(),
        modifier = Modifier
            .fillMaxSize()
            .pointerInput(Unit) {
                detectDragGestures { change, dragAmount ->
                    // Update progress based on drag
                }
            }
    ) {
        Box(modifier = Modifier.layoutId("box1"))
        Box(modifier = Modifier.layoutId("box2"))
    }
}
```

## 12. Push Notifications

### Firebase Cloud Messaging (FCM)
```kotlin
// FCM Service
class MyFirebaseMessagingService : FirebaseMessagingService() {

    override fun onMessageReceived(remoteMessage: RemoteMessage) {
        if (remoteMessage.data.isNotEmpty()) {
            val title = remoteMessage.data["title"] ?: "New Message"
            val body = remoteMessage.data["body"] ?: ""
            showNotification(title, body)
        }
    }

    override fun onNewToken(token: String) {
        Log.d("FCM", "New token: $token")
        // Send token to your server
        sendTokenToServer(token)
    }

    private fun showNotification(title: String, body: String) {
        val intent = Intent(this, MainActivity::class.java)
        val pendingIntent = PendingIntent.getActivity(
            this, 0, intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val notification = NotificationCompat.Builder(this, "default_channel")
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle(title)
            .setContentText(body)
            .setContentIntent(pendingIntent)
            .setAutoCancel(true)
            .build()

        NotificationManagerCompat.from(this)
            .notify(Random.nextInt(), notification)
    }
}

// Hilt module for FCM
@Module
@InstallIn(SingletonComponent::class)
object FcmModule {

    @Provides
    @Singleton
    fun provideFcmToken(): Flow<String> = flow {
        FirebaseMessaging.getInstance().token.addOnCompleteListener { task ->
            if (task.isSuccessful) {
                emit(task.result)
            }
        }
    }
}
```

## 13. Background Tasks

### WorkManager
```kotlin
// Background work
class SyncUserWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    @Inject
    lateinit var userRepository: UserRepository

    override suspend fun doWork(): Result = withContext(Dispatchers.IO) {
        return@withContext try {
            userRepository.syncUsers()
            Result.success()
        } catch (e: Exception) {
            if (runAttemptCount < 3) {
                Result.retry()
            } else {
                Result.failure()
            }
        }
    }
}

// Schedule work
class WorkScheduler @Inject constructor() {
    fun scheduleUserSync() {
        val syncWork = PeriodicWorkRequestBuilder<SyncUserWorker>(
            15, TimeUnit.MINUTES
        ).build()

        WorkManager.getInstance().enqueueUniquePeriodicWork(
            "user_sync",
            ExistingPeriodicWorkPolicy.KEEP,
            syncWork
        )
    }
}

// Foreground service
class DownloadService : Service() {

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val notification = NotificationCompat.Builder(this, "download_channel")
            .setSmallIcon(R.drawable.ic_download)
            .setContentTitle("Downloading...")
            .setProgress(100, 0, false)
            .build()

        startForeground(1, notification)

        CoroutineScope(Dispatchers.IO).launch {
            downloadFile()
        }

        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
```

## 14. Material Design 3

### Dynamic Color & Theming
```kotlin
@Composable
fun AppTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    useDynamicColor: Boolean = Build.VERSION.SDK_INT >= Build.VERSION_CODES.S,
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        useDynamicColor && darkTheme -> dynamicDarkColorScheme(LocalContext.current)
        useDynamicColor -> dynamicLightColorScheme(LocalContext.current)
        darkTheme -> darkColorScheme(
            primary = Purple80,
            secondary = PurpleGrey80,
            tertiary = Pink80
        )
        else -> lightColorScheme(
            primary = Purple40,
            secondary = PurpleGrey40,
            tertiary = Pink40
        )
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography(),
        content = content
    )
}

@Composable
fun StyledButton(
    onClick: () -> Unit,
    text: String,
    modifier: Modifier = Modifier
) {
    Button(
        onClick = onClick,
        modifier = modifier.height(48.dp),
        shape = RoundedCornerShape(8.dp)
    ) {
        Text(text, style = MaterialTheme.typography.labelMedium)
    }
}
```

## 15. Distribution & Gradle

### App Bundle & Play Store
```gradle
// build.gradle.kts
android {
    compileSdk = 34

    defaultConfig {
        applicationId = "com.example.myapp"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "1.0.0"
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
            signingConfig = signingConfigs.getByName("release")
        }
    }

    bundle {
        language.enableSplit = true
        density.enableSplit = true
        abi.enableSplit = true
    }
}

dependencies {
    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.lifecycle.viewmodel.ktx)
    implementation(libs.androidx.compose.ui)
    implementation(libs.androidx.hilt.navigation.compose)
    implementation(libs.hilt.android)
    kaptRelease(libs.hilt.compiler)
    implementation(libs.retrofit)
    implementation(libs.room.runtime)
    kaptRelease(libs.room.compiler)
}
```

## Key Best Practices

1. **Use StateFlow** for UI state in ViewModels
2. **Prefer suspending functions** over callbacks
3. **Apply baseline profiles** for startup performance
4. **Use Hilt** for dependency injection
5. **Implement proper error handling** with sealed classes
6. **Test with MockK** and Espresso
7. **Optimize recomposition** with stable annotations
8. **Use type-safe navigation** with serialization
9. **Implement proper scope management** with viewModelScope
10. **Bundle apps for Play Store** distribution

---

**Last Updated**: 2026-03-03
**Kotlin**: 1.9+
**Compose**: 1.6+
**Minimum SDK**: 24
**Target SDK**: 34
