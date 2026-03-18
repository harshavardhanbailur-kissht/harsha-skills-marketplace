# Mobile Data Storage Reference

Complete guide to data persistence patterns, frameworks, and best practices across iOS and Android platforms with cross-platform considerations.

## Table of Contents

- [1. SQLite/Room (Android)](#1-sqliteroom-android)
- [2. Core Data/SwiftData (iOS)](#2-core-dataswiftdata-ios)
- [3. Realm](#3-realm)
- [4. SQLDelight](#4-sqldelight)
- [5. Key-Value Storage](#5-key-value-storage)
- [6. Encrypted Storage](#6-encrypted-storage)
- [7. File Storage](#7-file-storage)
- [8. Cloud Sync](#8-cloud-sync)
- [9. Schema Versioning & Migration](#9-schema-versioning--migration)
- [10. Reactive Data](#10-reactive-data)
- [11. Caching Strategies](#11-caching-strategies)
- [12. Data Serialization](#12-data-serialization)

---

## 1. SQLite/Room (Android)

Room is the recommended abstraction layer over SQLite for Android apps.

### Entity Definition
```kotlin
@Entity(tableName = "users")
data class User(
    @PrimaryKey(autoGenerate = true)
    val id: Int = 0,
    val name: String,
    val email: String,
    @ColumnInfo(name = "created_at")
    val createdAt: Long = System.currentTimeMillis()
)

@Entity(
    tableName = "posts",
    foreignKeys = [
        ForeignKey(
            entity = User::class,
            parentColumns = ["id"],
            childColumns = ["userId"],
            onDelete = ForeignKey.CASCADE
        )
    ]
)
data class Post(
    @PrimaryKey(autoGenerate = true)
    val id: Int = 0,
    val userId: Int,
    val title: String,
    val content: String
)
```

### DAO (Data Access Object)
```kotlin
@Dao
interface UserDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUser(user: User)

    @Update
    suspend fun updateUser(user: User)

    @Delete
    suspend fun deleteUser(user: User)

    @Query("SELECT * FROM users WHERE id = :userId")
    suspend fun getUserById(userId: Int): User?

    @Query("SELECT * FROM users")
    fun getAllUsers(): Flow<List<User>>

    @Query("SELECT * FROM users ORDER BY created_at DESC")
    fun getUsersWithPosts(): Flow<List<UserWithPosts>>
}

@Dao
interface PostDao {
    @Insert
    suspend fun insertPost(post: Post)

    @Query("SELECT * FROM posts WHERE userId = :userId")
    fun getUserPosts(userId: Int): Flow<List<Post>>
}
```

### Relationships and Embedded Objects
```kotlin
// One-to-many relationship
data class UserWithPosts(
    @Embedded
    val user: User,
    @Relation(
        parentColumn = "id",
        entityColumn = "userId"
    )
    val posts: List<Post>
)

// Many-to-many relationship (junction table)
@Entity(
    primaryKeys = ["userId", "tagId"],
    foreignKeys = [
        ForeignKey(entity = User::class, parentColumns = ["id"], childColumns = ["userId"]),
        ForeignKey(entity = Tag::class, parentColumns = ["id"], childColumns = ["tagId"])
    ]
)
data class UserTagCrossRef(
    val userId: Int,
    val tagId: Int
)

data class UserWithTags(
    @Embedded
    val user: User,
    @Relation(
        parentColumn = "id",
        childColumn = "id",
        associateBy = Junction(UserTagCrossRef::class)
    )
    val tags: List<Tag>
)

// Embedded objects
data class Address(
    val street: String,
    val city: String,
    val zipCode: String
)

@Entity
data class Company(
    @PrimaryKey
    val id: Int,
    @Embedded
    val address: Address
)
```

### TypeConverters
```kotlin
class Converters {
    @TypeConverter
    fun fromTimestamp(value: Long?): LocalDateTime? {
        return value?.let {
            LocalDateTime.ofInstant(Instant.ofEpochMilli(it), ZoneId.systemDefault())
        }
    }

    @TypeConverter
    fun dateToTimestamp(date: LocalDateTime?): Long? {
        return date?.atZone(ZoneId.systemDefault())?.toInstant()?.toEpochMilli()
    }

    @TypeConverter
    fun fromJsonList(value: String?): List<String>? {
        return value?.let { Json.decodeFromString(it) }
    }

    @TypeConverter
    fun listToJson(value: List<String>?): String? {
        return value?.let { Json.encodeToString(it) }
    }
}
```

### Database and Migration
```kotlin
@Database(
    entities = [User::class, Post::class, Tag::class],
    version = 3,
    autoMigrations = [
        AutoMigration(from = 1, to = 2),
        AutoMigration(from = 2, to = 3, spec = Migration2to3::class)
    ]
)
@TypeConverters(Converters::class)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
    abstract fun postDao(): PostDao

    companion object {
        private var instance: AppDatabase? = null

        fun getInstance(context: Context): AppDatabase {
            return instance ?: synchronized(this) {
                Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "app_database"
                )
                    .addMigrations(Migration1to2(), Migration2to3())
                    .build()
                    .also { instance = it }
            }
        }
    }
}

// Manual migration for schema changes
object Migration1to2 : Migration(1, 2) {
    override fun migrate(database: SupportSQLiteDatabase) {
        database.execSQL(
            "ALTER TABLE users ADD COLUMN phone_number TEXT DEFAULT ''"
        )
    }
}

@RenameColumn.Entries(
    RenameColumn(tableName = "users", fromColumnName = "email", toColumnName = "email_address")
)
class Migration2to3 : AutoMigrationSpec
```

## 2. Core Data/SwiftData (iOS)

SwiftData is the modern replacement for Core Data, offering a simpler API with native Swift integration.

### SwiftData Models
```swift
import SwiftData

@Model
final class User {
    @Attribute(.unique)
    var id: String
    var name: String
    var email: String
    @Attribute(.externalStorage)
    var profileImage: Data?
    var createdDate: Date

    @Relationship(deleteRule: .cascade, inverse: \Post.author)
    var posts: [Post] = []

    init(id: String, name: String, email: String) {
        self.id = id
        self.name = name
        self.email = email
        self.createdDate = Date()
    }
}

@Model
final class Post {
    @Attribute(.unique)
    var id: String
    var title: String
    var content: String
    var createdDate: Date
    var author: User?

    @Relationship(deleteRule: .cascade, inverse: \Comment.post)
    var comments: [Comment] = []

    init(id: String, title: String, content: String) {
        self.id = id
        self.title = title
        self.content = content
        self.createdDate = Date()
    }
}

@Model
final class Comment {
    @Attribute(.unique)
    var id: String
    var text: String
    var post: Post?

    init(id: String, text: String) {
        self.id = id
        self.text = text
    }
}
```

### Queries and Predicates
```swift
import SwiftUI

struct ContentView: View {
    @Query(sort: \.createdDate, order: .reverse)
    var users: [User]

    // Filtered query
    @Query(
        filter: #Predicate<User> { user in
            user.email.contains("@example.com")
        },
        sort: \.name
    )
    var exampleUsers: [User]

    // Complex predicate
    @Query(
        filter: #Predicate<Post> { post in
            post.createdDate > Date().addingTimeInterval(-86400) &&
            post.author?.name.contains("John") == true
        }
    )
    var recentPostsByJohn: [Post]

    var body: some View {
        List {
            ForEach(users) { user in
                VStack(alignment: .leading) {
                    Text(user.name).font(.headline)
                    Text(user.email).font(.caption)
                }
            }
        }
    }
}
```

### Relationships and Cascading
```swift
@Model
final class Category {
    var name: String
    @Relationship(deleteRule: .cascade, inverse: \Item.category)
    var items: [Item] = []

    init(name: String) {
        self.name = name
    }
}

@Model
final class Item {
    var title: String
    var category: Category?

    init(title: String, category: Category? = nil) {
        self.title = title
        self.category = category
    }
}
```

### SwiftData Configuration and Migration
```swift
import SwiftData

// Configure and create ModelContainer
let container = try ModelContainer(
    for: User.self, Post.self, Comment.self,
    configurations: ModelConfiguration(
        schema: .init(
            [User.self, Post.self, Comment.self]
        ),
        isStoredInMemoryOnly: false,
        cloudKitDatabase: .private
    )
)

// Custom model context for transactions
let context = ModelContext(container)
context.autosaveEnabled = true

// Migration handling with VersionedSchema
enum UsersSchemaV1: VersionedSchema {
    static var models: [any PersistentModel.Type] {
        [User.self, Post.self]
    }

    @Model
    final class User {
        var id: String
        var name: String
    }

    @Model
    final class Post {
        var id: String
        var title: String
    }
}

enum UsersSchemaV2: VersionedSchema {
    static var models: [any PersistentModel.Type] {
        [User.self, Post.self]
    }

    @Model
    final class User {
        var id: String
        var name: String
        var email: String // Added field
    }

    @Model
    final class Post {
        var id: String
        var title: String
    }
}

enum UsersSchemaV3: VersionedSchema {
    static var models: [any PersistentModel.Type] {
        [User.self, Post.self]
    }

    @Model
    final class User {
        var id: String
        var name: String
        var email: String
    }

    @Model
    final class Post {
        var id: String
        var title: String
        var author: User? // Added relationship
    }
}

extension UsersSchemaV2 {
    static var migrationPlan: SchemaMigrationPlan {
        VersionedSchema.MigrationPlan(
            from: UsersSchemaV1,
            to: UsersSchemaV3,
            stages: [
                MigrationStage(
                    toVersion: UsersSchemaV2,
                    stage: {
                        // Migration logic
                    }
                ),
                MigrationStage(
                    toVersion: UsersSchemaV3,
                    stage: {
                        // Migration logic
                    }
                )
            ]
        )
    }
}
```

## 3. Realm

Cross-platform database with live objects and reactive queries.

### Realm Models
```kotlin
import io.realm.kotlin.ext.realmListOf
import io.realm.kotlin.types.RealmObject
import io.realm.kotlin.types.annotations.PrimaryKey

class User : RealmObject {
    @PrimaryKey
    var id: ObjectId = ObjectId.create()
    var name: String = ""
    var email: String = ""
    var createdAt: Long = System.currentTimeMillis()
    var posts: RealmList<Post> = realmListOf()
    var profileImage: RealmAny? = null
}

class Post : RealmObject {
    @PrimaryKey
    var id: ObjectId = ObjectId.create()
    var title: String = ""
    var content: String = ""
    var author: User? = null
    var comments: RealmList<Comment> = realmListOf()
}

class Comment : RealmObject {
    @PrimaryKey
    var id: ObjectId = ObjectId.create()
    var text: String = ""
    var post: Post? = null
    var createdAt: Long = System.currentTimeMillis()
}
```

### Realm Queries and Transactions
```kotlin
// Initialize Realm
val config = RealmConfiguration.Builder(setOf(User::class, Post::class, Comment::class))
    .schemaVersion(2)
    .migration { oldRealm, newRealm, oldSchema, newSchema ->
        // Migration logic
    }
    .build()

val realm = Realm.open(config)

// CRUD Operations
lifecycleScope.launch {
    // Create
    realm.write {
        val newUser = User().apply {
            name = "John Doe"
            email = "john@example.com"
        }
        copyToRealm(newUser)
    }

    // Read
    val users: RealmResults<User> = realm.query<User>().find()
    val user: User? = realm.query<User>("id == $0", userId).first().find()

    // Update
    realm.write {
        val user = query<User>("id == $0", userId).first().find()
        user?.name = "Updated Name"
    }

    // Delete
    realm.write {
        val user = query<User>("id == $0", userId).first().find()
        user?.let { delete(it) }
    }
}

// Live queries and reactive streams
realm.query<User>()
    .asFlow()
    .collect { users ->
        updateUI(users)
    }

// Complex queries
realm.query<Post>(
    "author.name CONTAINS[c] $0 AND createdAt > $1",
    "john",
    System.currentTimeMillis() - 86400000
).find()
```

## 4. SQLDelight

Type-safe SQL for Kotlin Multiplatform projects.

### SQL Definitions
```sql
-- Users.sq
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    created_at INTEGER NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE post (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);

-- Queries
insertUser:
INSERT INTO user(name, email)
VALUES (?, ?);

getUserById:
SELECT * FROM user WHERE id = ?;

getAllUsers:
SELECT * FROM user ORDER BY created_at DESC;

updateUserName:
UPDATE user SET name = ? WHERE id = ?;

deleteUser:
DELETE FROM user WHERE id = ?;

getUserPosts:
SELECT p.* FROM post p
INNER JOIN user u ON p.user_id = u.id
WHERE u.id = ?
ORDER BY p.created_at DESC;
```

### Kotlin Integration
```kotlin
import com.example.db.Database

// Initialize database
val sqlDriver: SqlDriver = AndroidSqliteDriver(Database.Schema, context, "app.db")
val database = Database(sqlDriver)

// Use generated queries
database.userQueries.insertUser(name = "John Doe", email = "john@example.com")

val user: User? = database.userQueries.getUserById(1).executeAsOneOrNull()

val allUsers: List<User> = database.userQueries.getAllUsers().executeAsList()

database.userQueries.updateUserName("Updated Name", 1)

database.userQueries.deleteUser(1)

// Flow integration for reactive queries
database.userQueries.getAllUsers()
    .asFlow()
    .map { it.executeAsList() }
    .collect { users ->
        updateUI(users)
    }
```

## 5. Key-Value Storage

Simple storage for preferences, settings, and small data.

### Android: SharedPreferences
```kotlin
// Basic SharedPreferences
val sharedPref = context.getSharedPreferences("app_prefs", Context.MODE_PRIVATE)

sharedPref.edit().apply {
    putString("user_name", "John Doe")
    putInt("user_id", 123)
    putBoolean("is_logged_in", true)
    putLong("last_sync", System.currentTimeMillis())
    apply()
}

val userName = sharedPref.getString("user_name", "Unknown")
val isLoggedIn = sharedPref.getBoolean("is_logged_in", false)

// Encrypted SharedPreferences
val encryptedSharedPreferences = EncryptedSharedPreferences.create(
    "secret_prefs",
    MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build(),
    context,
    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
)

encryptedSharedPreferences.edit().apply {
    putString("api_token", "secret_token_123")
    apply()
}
```

### Android: DataStore
```kotlin
// Proto DataStore for type-safe storage
val appPreferencesStore = DataStoreFactory.create(
    serializer = AppSettingsSerializer,
    produceFile = { context.preferencesDataStoreFile("app_settings") }
)

// Usage
val userPreferences: Flow<AppSettings> = appPreferencesStore.data

userPreferences.collect { settings ->
    println("Theme: ${settings.theme}")
}

// Update data
appPreferencesStore.updateData { currentSettings ->
    currentSettings.toBuilder()
        .setTheme("dark")
        .setLanguage("en")
        .build()
}
```

### iOS: UserDefaults
```swift
let defaults = UserDefaults.standard

// Save data
defaults.set("John Doe", forKey: "user_name")
defaults.set(123, forKey: "user_id")
defaults.set(true, forKey: "is_logged_in")
defaults.set(Date(), forKey: "last_sync")

// Retrieve data
let userName = defaults.string(forKey: "user_name") ?? "Unknown"
let isLoggedIn = defaults.bool(forKey: "is_logged_in")

// Save complex objects
let userData: [String: Any] = ["name": "John", "age": 30]
defaults.set(userData, forKey: "user_data")

// Codable support
struct UserSettings: Codable {
    var theme: String
    var language: String
}

let settings = UserSettings(theme: "dark", language: "en")
let encoded = try JSONEncoder().encode(settings)
defaults.set(encoded, forKey: "settings")

if let data = defaults.data(forKey: "settings") {
    let decoded = try JSONDecoder().decode(UserSettings.self, from: data)
}
```

### React Native: AsyncStorage
```javascript
import AsyncStorage from '@react-native-async-storage/async-storage';

// Store data
const storeUserData = async () => {
    try {
        await AsyncStorage.setItem('user_name', 'John Doe');
        await AsyncStorage.setItem('user_id', '123');
        await AsyncStorage.setItem('user_data', JSON.stringify({
            name: 'John',
            age: 30
        }));
    } catch (error) {
        console.error('Failed to store data:', error);
    }
};

// Retrieve data
const retrieveUserData = async () => {
    try {
        const name = await AsyncStorage.getItem('user_name');
        const userData = await AsyncStorage.getItem('user_data');
        const parsed = userData ? JSON.parse(userData) : null;
    } catch (error) {
        console.error('Failed to retrieve data:', error);
    }
};

// Multi-set for atomic operations
await AsyncStorage.multiSet([
    ['theme', 'dark'],
    ['language', 'en'],
    ['notifications', 'true']
]);
```

### MMKV (Android high-performance key-value)
```kotlin
import com.tencent.mmkv.MMKV

// Initialize MMKV
MMKV.initialize(context)
val kv = MMKV.defaultMMKV()

// Store data
kv.encode("user_name", "John Doe")
kv.encode("user_id", 123)
kv.encode("is_premium", true)
kv.encode("scores", intArrayOf(10, 20, 30))

// Retrieve data
val userName = kv.decodeString("user_name", "Unknown")
val userId = kv.decodeInt("user_id", 0)
val scores = kv.decodeIntArray("scores")

// Parcelable support
val user = User("John", 30)
kv.encode("user", user)
val retrievedUser = kv.decodeParcelable("user", User::class.java)
```

## 6. Encrypted Storage

Secure storage for sensitive information.

### iOS: Keychain
```swift
import Security

class KeychainManager {
    static let shared = KeychainManager()

    func save(key: String, value: String) throws {
        guard let data = value.data(using: .utf8) else { return }

        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecValueData as String: data
        ]

        SecItemDelete(query as CFDictionary)
        let status = SecItemAdd(query as CFDictionary, nil)

        guard status == errSecSuccess else {
            throw KeychainError.saveFailed
        }
    }

    func retrieve(key: String) throws -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecReturnData as String: true
        ]

        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)

        guard status == errSecSuccess,
              let data = result as? Data,
              let string = String(data: data, encoding: .utf8) else {
            return nil
        }

        return string
    }

    func delete(key: String) throws {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key
        ]

        let status = SecItemDelete(query as CFDictionary)
        guard status == errSecSuccess else {
            throw KeychainError.deleteFailed
        }
    }
}

// Usage
try KeychainManager.shared.save(key: "api_token", value: "secret_token_123")
if let token = try KeychainManager.shared.retrieve(key: "api_token") {
    print("Token: \(token)")
}
```

### Android: Keystore
```kotlin
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import javax.crypto.Cipher
import javax.crypto.KeyGenerator

class KeystoreManager {
    private val keyStore = KeyStore.getInstance("AndroidKeyStore").apply {
        load(null)
    }

    fun generateKey(keyAlias: String) {
        val keyGenerator = KeyGenerator.getInstance(
            KeyProperties.KEY_ALGORITHM_AES,
            "AndroidKeyStore"
        )

        keyGenerator.init(
            KeyGenParameterSpec.Builder(
                keyAlias,
                KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
            )
                .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                .build()
        )

        keyGenerator.generateKey()
    }

    fun encryptData(keyAlias: String, plainText: String): ByteArray {
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        val key = keyStore.getKey(keyAlias, null) as SecretKey
        cipher.init(Cipher.ENCRYPT_MODE, key)
        return cipher.doFinal(plainText.toByteArray())
    }

    fun decryptData(keyAlias: String, encryptedData: ByteArray): String {
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        val key = keyStore.getKey(keyAlias, null) as SecretKey
        cipher.init(Cipher.DECRYPT_MODE, key)
        val decryptedData = cipher.doFinal(encryptedData)
        return String(decryptedData)
    }
}
```

### EncryptedSharedPreferences
```kotlin
val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .build()

val encryptedSharedPrefs = EncryptedSharedPreferences.create(
    context,
    "secret_prefs",
    masterKey,
    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
)

encryptedSharedPrefs.edit().apply {
    putString("auth_token", "secret_token")
    putString("refresh_token", "refresh_secret")
    apply()
}
```

## 7. File Storage

Structured file access and caching.

### iOS: Documents and Cache
```swift
class FileStorageManager {
    static let shared = FileStorageManager()

    var documentsURL: URL {
        FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
    }

    var cachesURL: URL {
        FileManager.default.urls(for: .cachesDirectory, in: .userDomainMask)[0]
    }

    func saveToDocuments(filename: String, data: Data) throws {
        let fileURL = documentsURL.appendingPathComponent(filename)
        try data.write(to: fileURL, options: .atomic)
    }

    func loadFromDocuments(filename: String) throws -> Data {
        let fileURL = documentsURL.appendingPathComponent(filename)
        return try Data(contentsOf: fileURL)
    }

    func saveToCache(filename: String, data: Data) throws {
        let fileURL = cachesURL.appendingPathComponent(filename)
        try data.write(to: fileURL, options: .atomic)
    }

    func clearCache() throws {
        let fileManager = FileManager.default
        let cacheFiles = try fileManager.contentsOfDirectory(at: cachesURL, includingPropertiesForKeys: nil)
        for file in cacheFiles {
            try fileManager.removeItem(at: file)
        }
    }
}

// App Groups for sharing between app and extensions
let appGroupsURL = FileManager.default.containerURL(forSecurityApplicationGroupIdentifier: "group.com.example.app")
let sharedFile = appGroupsURL?.appendingPathComponent("shared_data.json")
```

### Android: Scoped Storage and Cache
```kotlin
// Save to app-specific directory (no permissions needed)
val fileName = "user_profile.json"
val fileContent = """{"name":"John","age":30}"""

// Internal storage (app-specific)
context.openFileOutput(fileName, Context.MODE_PRIVATE).use {
    it.write(fileContent.toByteArray())
}

// Read from internal storage
context.openFileInput(fileName).bufferedReader().use {
    val content = it.readText()
}

// Cache directory (can be cleared by system)
val cacheFile = File(context.cacheDir, "temp_data.tmp")
cacheFile.writeText(fileContent)

// External files directory (Documents equivalent)
val documentsDir = context.getExternalFilesDir(Environment.DIRECTORY_DOCUMENTS)
val docFile = File(documentsDir, "document.pdf")
docFile.writeBytes(pdfBytes)

// Scoped storage for media files (API 30+)
val contentValues = ContentValues().apply {
    put(MediaStore.Images.Media.DISPLAY_NAME, "photo.jpg")
    put(MediaStore.Images.Media.MIME_TYPE, "image/jpeg")
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
        put(MediaStore.Images.Media.RELATIVE_PATH, Environment.DIRECTORY_PICTURES)
    }
}

val resolver = context.contentResolver
val imageUri = resolver.insert(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, contentValues)
```

## 8. Cloud Sync

Syncing data between local storage and cloud backends.

### iOS: CloudKit
```swift
import CloudKit

class CloudKitManager {
    let container = CKContainer.default()
    let database = CKContainer.default().privateCloudDatabase

    func saveUserToCloud(user: User) async throws {
        let record = CKRecord(recordType: "User")
        record["name"] = user.name
        record["email"] = user.email
        record["createdDate"] = user.createdDate

        _ = try await database.save(record)
    }

    func fetchUsersFromCloud() async throws -> [User] {
        let predicate = NSPredicate(value: true)
        let query = CKQuery(recordType: "User", predicate: predicate)
        query.sortDescriptors = [NSSortDescriptor(key: "createdDate", ascending: false)]

        let results = try await database.records(matching: query)
        return results.matchResults.compactMap { _, result in
            guard let record = try? result.get() else { return nil }
            return User(
                id: record.recordID.recordName,
                name: record["name"] ?? "",
                email: record["email"] ?? ""
            )
        }
    }

    func syncChanges() {
        let zone = CKRecordZone.default()
        let token: CKServerChangeToken? = nil // Retrieve from UserDefaults

        database.fetchChanges(
            inRecordZone: zone.zoneID,
            since: token
        ) { serverChangeToken, error in
            if let error = error {
                print("Sync error: \(error)")
                return
            }

            // Save token for next sync
            UserDefaults.standard.set(serverChangeToken, forKey: "cloudkit_token")
        }
    }
}
```

### Firebase Firestore Offline Persistence
```kotlin
import com.google.firebase.firestore.FirebaseFirestore
import com.google.firebase.firestore.PersistentCacheSettings

val settings = FirebaseFirestoreSettings.Builder()
    .setCacheSizeBytes(FirebaseFirestoreSettings.CACHE_SIZE_UNLIMITED)
    .build()

val db = FirebaseFirestore.getInstance()
db.firestoreSettings = settings

// Listen for documents with offline support
db.collection("users").document(userId)
    .addSnapshotListener { snapshot, error ->
        if (snapshot != null) {
            val user = snapshot.toObject(User::class.java)
            println("Data from ${if (snapshot.metadata.isFromCache) "cache" else "server"}")
        }
    }

// Write data
db.collection("users").document(userId).set(user)
    .addOnSuccessListener {
        println("Data synced to cloud")
    }
```

### Supabase Local-First Sync
```kotlin
import io.github.jan.supabase.createSupabaseClient
import io.github.jan.supabase.postgrest.Postgrest
import io.github.jan.supabase.realtime.Realtime

val supabase = createSupabaseClient(
    supabaseUrl = "https://project.supabase.co",
    supabaseKey = "anon-key"
) {
    install(Postgrest)
    install(Realtime)
}

// Query with local caching
lifecycleScope.launch {
    val users = supabase.from("users").select().decodeList<User>()

    // Listen for real-time updates
    supabase.realtime.channel("public:users").subscribe { changeEvent ->
        when (changeEvent.type) {
            "INSERT" -> handleUserInserted(changeEvent.new())
            "UPDATE" -> handleUserUpdated(changeEvent.new())
            "DELETE" -> handleUserDeleted(changeEvent.old())
        }
    }
}
```

## 9. Schema Versioning & Migration

Managing database schema changes over app versions.

### Room Auto-Migration
```kotlin
@Database(
    entities = [User::class, Post::class],
    version = 3,
    autoMigrations = [
        AutoMigration(from = 1, to = 2),
        AutoMigration(from = 2, to = 3, spec = Migration2to3::class)
    ]
)
abstract class AppDatabase : RoomDatabase()

// Auto-migration doesn't require manual SQL for simple changes
// Automatic handling of:
// - Adding nullable columns
// - Adding tables
// - Adding indices

@RenameColumn.Entries(
    RenameColumn(tableName = "users", fromColumnName = "email", toColumnName = "email_address")
)
class Migration2to3 : AutoMigrationSpec {
    // For complex changes, provide a spec
    override fun onPostMigrate(db: SupportSQLiteDatabase) {
        // Post-migration cleanup
    }
}
```

### Manual Room Migration
```kotlin
val migration3to4 = object : Migration(3, 4) {
    override fun migrate(database: SupportSQLiteDatabase) {
        // Add new table
        database.execSQL(
            "CREATE TABLE IF NOT EXISTS tags (id INTEGER PRIMARY KEY, name TEXT)"
        )

        // Add column with default
        database.execSQL(
            "ALTER TABLE posts ADD COLUMN tag_id INTEGER DEFAULT NULL"
        )

        // Add foreign key constraint
        database.execSQL(
            "CREATE TABLE posts_new (id INTEGER PRIMARY KEY, tag_id INTEGER, FOREIGN KEY(tag_id) REFERENCES tags(id))"
        )
    }
}

val database = Room.databaseBuilder(context, AppDatabase::class.java, "db")
    .addMigrations(migration3to4)
    .build()
```

### Core Data Lightweight Migration
```swift
// Core Data lightweight migration handles:
// - Adding new attributes with default values
// - Removing attributes
// - Renaming entities or attributes
// - Changing optional/required status

// Model versioning
extension NSEntityDescription {
    static func createUserEntityV1() -> NSEntityDescription {
        let entity = NSEntityDescription()
        entity.name = "User"

        let id = NSAttributeDescription()
        id.name = "id"
        id.attributeType = .stringAttributeType
        id.isOptional = false

        let name = NSAttributeDescription()
        name.name = "name"
        name.attributeType = .stringAttributeType
        name.isOptional = false

        entity.properties = [id, name]
        return entity
    }
}

// Initiate migration
let migrationManager = NSMigrationManager(sourceModel: sourceModel, destinationModel: targetModel)
try migrationManager.migrateStore(from: sourceURL, sourceType: .sqlite, options: nil, with: targetURL, destinationType: .sqlite, options: nil)
```

## 10. Reactive Data

Reactive patterns for observing and responding to data changes.

### Android: Flow
```kotlin
@Dao
interface UserDao {
    @Query("SELECT * FROM users")
    fun getAllUsersFlow(): Flow<List<User>>

    @Query("SELECT * FROM users WHERE id = :userId")
    fun getUserFlow(userId: Int): Flow<User?>
}

// In repository
class UserRepository(private val userDao: UserDao) {
    val allUsers: Flow<List<User>> = userDao.getAllUsersFlow()

    fun getUserById(userId: Int): Flow<User?> = userDao.getUserFlow(userId)

    fun filteredUsers(query: String): Flow<List<User>> {
        return userDao.getAllUsersFlow()
            .map { users -> users.filter { it.name.contains(query) } }
            .catch { emit(emptyList()) }
    }
}

// In ViewModel
class UserViewModel(private val repository: UserRepository) : ViewModel() {
    val users: StateFlow<List<User>> = repository.allUsers
        .stateIn(viewModelScope, SharingStarted.Lazily, emptyList())
}

// In UI
LaunchedEffect(Unit) {
    viewModel.users.collect { users ->
        updateUI(users)
    }
}
```

### iOS: Combine
```swift
import Combine

class UserViewModel: ObservableObject {
    @Published var users: [User] = []
    @Published var selectedUser: User?

    private let userRepository: UserRepository
    private var cancellables: Set<AnyCancellable> = []

    init(repository: UserRepository) {
        self.userRepository = repository
        setupBindings()
    }

    private func setupBindings() {
        userRepository.getUsersPublisher()
            .receive(on: DispatchQueue.main)
            .assign(to: &$users)

        // Combine multiple publishers
        Publishers.CombineLatest(
            $users,
            $selectedUser
        )
        .map { users, selected in
            users.filter { $0.id != selected?.id }
        }
        .receive(on: DispatchQueue.main)
        .sink { otherUsers in
            print("Other users: \(otherUsers)")
        }
        .store(in: &cancellables)
    }
}

struct UserListView: View {
    @StateObject var viewModel = UserViewModel(repository: UserRepository())

    var body: some View {
        List {
            ForEach(viewModel.users) { user in
                Text(user.name)
            }
        }
        .task {
            viewModel.fetchUsers()
        }
    }
}
```

## 11. Caching Strategies

Efficient data caching and cache invalidation.

### LRU Cache Implementation
```kotlin
class LRUCache<K, V>(private val maxSize: Int) {
    private val cache = LinkedHashMap<K, V>(maxSize, 0.75f, true)

    fun get(key: K): V? = cache[key]

    fun put(key: K, value: V) {
        if (cache.containsKey(key)) {
            cache.remove(key)
        }

        if (cache.size >= maxSize) {
            cache.remove(cache.keys.first())
        }

        cache[key] = value
    }

    fun clear() = cache.clear()
}

// Usage with memory cache
val userCache = LRUCache<Int, User>(maxSize = 100)

fun getUserWithCache(userId: Int): User {
    userCache.get(userId)?.let { return it }

    val user = fetchUserFromDatabase(userId)
    userCache.put(userId, user)
    return user
}
```

### TTL Cache
```kotlin
class TTLCache<K, V>(private val ttlMillis: Long) {
    private data class CacheEntry<V>(val value: V, val expiresAt: Long)

    private val cache = mutableMapOf<K, CacheEntry<V>>()

    fun get(key: K): V? {
        val entry = cache[key] ?: return null

        return if (System.currentTimeMillis() < entry.expiresAt) {
            entry.value
        } else {
            cache.remove(key)
            null
        }
    }

    fun put(key: K, value: V) {
        cache[key] = CacheEntry(value, System.currentTimeMillis() + ttlMillis)
    }

    fun invalidate(key: K) {
        cache.remove(key)
    }

    fun invalidateAll() {
        cache.clear()
    }
}

// Cache invalidation patterns
class UserRepository(private val database: UserDatabase) {
    private val userCache = TTLCache<Int, User>(ttlMillis = 5 * 60 * 1000) // 5 minutes

    suspend fun getUser(userId: Int): User {
        userCache.get(userId)?.let { return it }

        val user = database.userDao().getUserById(userId)
        user?.let { userCache.put(userId, it) }
        return user ?: throw UserNotFoundException()
    }

    suspend fun updateUser(user: User) {
        database.userDao().updateUser(user)
        userCache.invalidate(user.id) // Invalidate cache
    }

    suspend fun deleteUser(userId: Int) {
        database.userDao().deleteUser(userId)
        userCache.invalidate(userId)
    }
}
```

### Cache Invalidation Strategies
```kotlin
// Strategy 1: Time-based invalidation
val imageCache = mutableMapOf<String, Pair<Bitmap, Long>>()

fun getCachedImage(url: String, maxAgeMillis: Long = 3600000): Bitmap? {
    val (bitmap, timestamp) = imageCache[url] ?: return null
    return if (System.currentTimeMillis() - timestamp < maxAgeMillis) {
        bitmap
    } else {
        imageCache.remove(url)
        null
    }
}

// Strategy 2: Event-based invalidation
class CacheInvalidationManager {
    private val invalidationEvents = MutableSharedFlow<String>()

    suspend fun invalidateCache(key: String) {
        invalidationEvents.emit(key)
    }

    fun watchInvalidations(): Flow<String> = invalidationEvents
}

// Strategy 3: Size-based eviction
class BoundedCache<K, V>(
    private val maxSize: Int,
    private val onEvict: (K, V) -> Unit = { _, _ -> }
) {
    private val cache = LinkedHashMap<K, V>(maxSize, 0.75f, false)

    fun put(key: K, value: V) {
        val previous = cache.put(key, value)
        previous?.let { onEvict(key, it) }

        if (cache.size > maxSize) {
            val iterator = cache.iterator()
            iterator.next()
            iterator.remove()
        }
    }
}
```

## 12. Data Serialization

Converting objects to/from portable formats.

### Codable (Swift)
```swift
struct User: Codable {
    let id: String
    let name: String
    let email: String
    let createdDate: Date

    enum CodingKeys: String, CodingKey {
        case id, name, email
        case createdDate = "created_at"
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        self.id = try container.decode(String.self, forKey: .id)
        self.name = try container.decode(String.self, forKey: .name)
        self.email = try container.decode(String.self, forKey: .email)

        let timestamp = try container.decode(Double.self, forKey: .createdDate)
        self.createdDate = Date(timeIntervalSince1970: timestamp)
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(id, forKey: .id)
        try container.encode(name, forKey: .name)
        try container.encode(email, forKey: .email)
        try container.encode(createdDate.timeIntervalSince1970, forKey: .createdDate)
    }
}

// Serialization
let user = User(id: "1", name: "John", email: "john@example.com", createdDate: Date())
let jsonData = try JSONEncoder().encode(user)
let jsonString = String(data: jsonData, encoding: .utf8)

// Deserialization
let decodedUser = try JSONDecoder().decode(User.self, from: jsonData)
```

### kotlinx.serialization (Kotlin)
```kotlin
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json

@Serializable
data class User(
    val id: String,
    val name: String,
    val email: String,
    @Serializable(with = DateSerializer::class)
    val createdDate: LocalDateTime
)

@Serializable
data class Post(
    val id: String,
    val title: String,
    val content: String,
    val author: User
)

// Custom serializer for complex types
object DateSerializer : KSerializer<LocalDateTime> {
    override val descriptor = PrimitiveSerialDescriptor("LocalDateTime", PrimitiveKind.STRING)

    override fun serialize(encoder: Encoder, value: LocalDateTime) {
        encoder.encodeString(value.toString())
    }

    override fun deserialize(decoder: Decoder): LocalDateTime {
        return LocalDateTime.parse(decoder.decodeString())
    }
}

// Serialization
val user = User("1", "John", "john@example.com", LocalDateTime.now())
val jsonString = Json.encodeToString(user)

// Deserialization
val decodedUser = Json.decodeFromString<User>(jsonString)

// Pretty printing
val prettyJson = Json { prettyPrint = true }
val formatted = prettyJson.encodeToString(user)
```

### Protocol Buffers
```protobuf
syntax = "proto3";

message User {
    string id = 1;
    string name = 2;
    string email = 3;
    int64 created_at = 4;
}

message Post {
    string id = 1;
    string title = 2;
    string content = 3;
    User author = 4;
    repeated string tags = 5;
}
```

Usage in Kotlin:
```kotlin
// Serialization
val user = UserOuterClass.User.newBuilder()
    .setId("1")
    .setName("John")
    .setEmail("john@example.com")
    .setCreatedAt(System.currentTimeMillis())
    .build()

val bytes = user.toByteArray()

// Deserialization
val decodedUser = UserOuterClass.User.parseFrom(bytes)
```

---

**References:**
- Room: https://developer.android.com/training/data-storage/room
- SwiftData: https://developer.apple.com/documentation/SwiftData
- Realm: https://www.realm.io
- SQLDelight: https://cashapp.github.io/sqldelight
- CloudKit: https://developer.apple.com/cloudkit
- Keychain Services: https://developer.apple.com/documentation/security/keychain_services
- Android Keystore: https://developer.android.com/training/articles/keystore
