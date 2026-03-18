# iOS Native Development Reference

A comprehensive guide to modern iOS development with production-ready Swift code examples, covering SwiftUI, async/await, data persistence, networking, and more.

## Table of Contents

- [Swift Modern Features](#swift-modern-features)
- [SwiftUI Core](#swiftui-core)
- [UIKit Interoperability](#uikit-interoperability)
- [Navigation](#navigation)
- [Data Persistence](#data-persistence)
- [Networking](#networking)
- [Architecture Patterns](#architecture-patterns)
- [Performance Optimization](#performance-optimization)
- [Testing](#testing)
- [Accessibility](#accessibility)
- [App Extensions](#app-extensions)
- [Push Notifications](#push-notifications)
- [Privacy & Security](#privacy--security)
- [App Distribution](#app-distribution)
- [Production Checklist](#production-checklist)
- [References](#references)

---

## Swift Modern Features

### Async/Await Pattern

```swift
// Modern async/await for cleaner asynchronous code
func fetchUserData(id: String) async throws -> User {
    let url = URL(string: "https://api.example.com/users/\(id)")!
    let (data, _) = try await URLSession.shared.data(from: url)
    return try JSONDecoder().decode(User.self, from: data)
}

// Usage in async context
Task {
    do {
        let user = try await fetchUserData(id: "123")
        print("User: \(user.name)")
    } catch {
        print("Error: \(error)")
    }
}
```

### Actors for Thread Safety

```swift
// Actor provides thread-safe access to mutable state
actor UserCache {
    private var cache: [String: User] = [:]

    func getUser(_ id: String) -> User? {
        cache[id]
    }

    func setUser(_ user: User) {
        cache[user.id] = user
    }

    func clear() {
        cache.removeAll()
    }
}

// Thread-safe usage
let cache = UserCache()
Task {
    await cache.setUser(User(id: "1", name: "Alice"))
    if let user = await cache.getUser("1") {
        print("Found user: \(user.name)")
    }
}
```

### Structured Concurrency

```swift
// Spawn multiple concurrent tasks
func loadDashboard() async throws -> Dashboard {
    async let users = fetchUsers()
    async let posts = fetchPosts()
    async let comments = fetchComments()

    return try await Dashboard(
        users: users,
        posts: posts,
        comments: comments
    )
}

// TaskGroup for dynamic task creation
func downloadMultipleFiles(_ urls: [URL]) async throws -> [Data] {
    return try await withThrowingTaskGroup(of: Data.self) { group in
        var results: [Data] = []

        for url in urls {
            group.addTask {
                let (data, _) = try await URLSession.shared.data(from: url)
                return data
            }
        }

        for try await data in group {
            results.append(data)
        }

        return results
    }
}
```

### @Observable Macro

```swift
import Observation

@Observable
final class AppViewModel {
    var isLoading = false
    var errorMessage: String?
    var users: [User] = []

    func loadUsers() async {
        isLoading = true
        defer { isLoading = false }

        do {
            users = try await UserService.shared.fetchUsers()
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}

// SwiftUI integration
struct UserListView: View {
    @State var viewModel = AppViewModel()

    var body: some View {
        if viewModel.isLoading {
            ProgressView()
        } else if let error = viewModel.errorMessage {
            Text("Error: \(error)")
        } else {
            List(viewModel.users) { user in
                Text(user.name)
            }
        }
    }
}
```

### Property Wrappers

```swift
// Custom property wrapper for clamped values
@propertyWrapper
struct Clamped<Value: Comparable> {
    private var value: Value
    private let range: ClosedRange<Value>

    var wrappedValue: Value {
        get { value }
        set { value = min(max(newValue, range.lowerBound), range.upperBound) }
    }

    init(wrappedValue: Value, _ range: ClosedRange<Value>) {
        self.range = range
        self.value = min(max(wrappedValue, range.lowerBound), range.upperBound)
    }
}

struct ProgressModel {
    @Clamped(0...100) var percentage = 50
}

var progress = ProgressModel()
progress.percentage = 150  // Automatically clamped to 100
```

### Result Builders

```swift
@resultBuilder
struct ViewBuilder {
    static func buildBlock(_ views: View...) -> some View {
        VStack(spacing: 8) {
            ForEach(0..<views.count, id: \.self) { index in
                views[index]
            }
        }
    }
}

// DSL for building view hierarchies
func createLayout() -> some View {
    @ViewBuilder
    func layout() -> some View {
        Text("Title")
            .font(.title)
        Divider()
        Text("Content")
            .font(.body)
    }
    return layout()
}
```

---

## SwiftUI Core

### State Management Hierarchy

```swift
// @State: local component state
struct CounterView: View {
    @State private var count = 0

    var body: some View {
        VStack {
            Text("Count: \(count)")
            Button("Increment") { count += 1 }
        }
    }
}

// @Binding: bidirectional connection
struct ChildView: View {
    @Binding var value: Int

    var body: some View {
        Stepper("Value: \(value)", value: $value)
    }
}

// @StateObject: observes reference type in SwiftUI
class DataModel: ObservableObject {
    @Published var items: [String] = []
}

struct ParentView: View {
    @StateObject private var model = DataModel()

    var body: some View {
        VStack {
            List(model.items, id: \.self) { item in
                Text(item)
            }
            Button("Add Item") {
                model.items.append("New Item")
            }
        }
    }
}

// @EnvironmentObject: pass data down view hierarchy
struct RootView: View {
    @StateObject private var appState = AppState()

    var body: some View {
        TabView {
            HomeView()
            SettingsView()
        }
        .environmentObject(appState)
    }
}

struct HomeView: View {
    @EnvironmentObject var appState: AppState

    var body: some View {
        Text("User: \(appState.currentUser?.name ?? "Unknown")")
    }
}
```

### Advanced View Modifiers

```swift
struct CustomButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(.headline)
            .foregroundColor(.white)
            .padding()
            .background(Color.blue)
            .cornerRadius(8)
            .opacity(configuration.isPressed ? 0.8 : 1.0)
            .scaleEffect(configuration.isPressed ? 0.98 : 1.0)
    }
}

// ViewModifier for reusable styling
struct ShadowModifier: ViewModifier {
    func body(content: Content) -> some View {
        content
            .shadow(color: Color.black.opacity(0.2), radius: 8, x: 0, y: 4)
    }
}

extension View {
    func shadowStyle() -> some View {
        modifier(ShadowModifier())
    }
}

struct ContentView: View {
    var body: some View {
        VStack(spacing: 16) {
            Text("Hello")
                .shadowStyle()

            Button("Tap Me") { }
                .buttonStyle(CustomButtonStyle())
        }
    }
}
```

---

## UIKit Interoperability

### UIViewRepresentable

```swift
struct TextViewRepresentable: UIViewRepresentable {
    @Binding var text: String

    func makeUIView(context: Context) -> UITextView {
        let textView = UITextView()
        textView.delegate = context.coordinator
        textView.font = UIFont.systemFont(ofSize: 16)
        return textView
    }

    func updateUIView(_ uiView: UITextView, context: Context) {
        uiView.text = text
    }

    func makeCoordinator() -> Coordinator {
        Coordinator(text: $text)
    }

    class Coordinator: NSObject, UITextViewDelegate {
        @Binding var text: String

        init(text: Binding<String>) {
            self._text = text
        }

        func textViewDidChange(_ textView: UITextView) {
            text = textView.text
        }
    }
}

struct TextEditorView: View {
    @State private var text = ""

    var body: some View {
        TextViewRepresentable(text: $text)
            .border(Color.gray)
    }
}
```

### UIViewControllerRepresentable

```swift
struct ImagePickerController: UIViewControllerRepresentable {
    @Binding var selectedImage: UIImage?
    @Environment(\.dismiss) var dismiss

    func makeUIViewController(context: Context) -> UIImagePickerController {
        let picker = UIImagePickerController()
        picker.delegate = context.coordinator
        picker.sourceType = .photoLibrary
        return picker
    }

    func updateUIViewController(_ uiViewController: UIImagePickerController, context: Context) {}

    func makeCoordinator() -> Coordinator {
        Coordinator(selectedImage: $selectedImage, dismiss: dismiss)
    }

    class Coordinator: NSObject, UIImagePickerControllerDelegate, UINavigationControllerDelegate {
        @Binding var selectedImage: UIImage?
        let dismiss: DismissAction

        init(selectedImage: Binding<UIImage?>, dismiss: DismissAction) {
            self._selectedImage = selectedImage
            self.dismiss = dismiss
        }

        func imagePickerController(_ picker: UIImagePickerController,
                                  didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey: Any]) {
            if let image = info[.originalImage] as? UIImage {
                selectedImage = image
            }
            dismiss()
        }
    }
}
```

---

## Navigation

### NavigationStack (iOS 16+)

```swift
enum NavigationDestination: Hashable {
    case userDetail(id: String)
    case settings
    case profile
}

struct MainNavigationView: View {
    @State private var navigationPath = NavigationPath()

    var body: some View {
        NavigationStack(path: $navigationPath) {
            VStack {
                List(1...10, id: \.self) { id in
                    NavigationLink("User \(id)", value: NavigationDestination.userDetail(id: "\(id)"))
                }

                Button("Go to Settings") {
                    navigationPath.append(NavigationDestination.settings)
                }
            }
            .navigationTitle("Home")
            .navigationDestination(for: NavigationDestination.self) { destination in
                switch destination {
                case .userDetail(let id):
                    UserDetailView(userId: id, navigationPath: $navigationPath)
                case .settings:
                    SettingsView()
                case .profile:
                    ProfileView()
                }
            }
        }
    }
}

struct UserDetailView: View {
    let userId: String
    @Binding var navigationPath: NavigationPath

    var body: some View {
        VStack {
            Text("User ID: \(userId)")
            Button("Go to Profile") {
                navigationPath.append(NavigationDestination.profile)
            }
            Button("Pop Back") {
                navigationPath.removeLast()
            }
        }
        .navigationTitle("User Detail")
        .navigationBarTitleDisplayMode(.inline)
    }
}
```

### Programmatic Navigation with Custom Router

```swift
@Observable
class Router {
    var path = NavigationPath()

    func navigate(to destination: NavigationDestination) {
        path.append(destination)
    }

    func popToRoot() {
        path.removeLast(path.count)
    }

    func pop() {
        path.removeLast()
    }
}

struct AppView: View {
    @State private var router = Router()

    var body: some View {
        NavigationStack(path: $router.path) {
            HomeView(router: router)
                .navigationDestination(for: NavigationDestination.self) { destination in
                    DetailView(destination: destination, router: router)
                }
        }
    }
}
```

---

## Data Persistence

### SwiftData (iOS 17+, Modern Approach)

```swift
import SwiftData

@Model
final class TodoItem {
    @Attribute(.unique) var id: String
    var title: String
    var description: String
    var isCompleted: Bool = false
    var createdDate: Date = Date()

    init(id: String, title: String, description: String) {
        self.id = id
        self.title = title
        self.description = description
    }
}

@Model
final class TodoList {
    @Attribute(.unique) var id: String
    var name: String
    @Relationship(deleteRule: .cascade, inverse: \TodoItem.list) var items: [TodoItem] = []

    init(id: String, name: String) {
        self.id = id
        self.name = name
    }
}

struct TodoView: View {
    @Query var todos: [TodoItem]
    @Environment(\.modelContext) var modelContext

    var body: some View {
        List {
            ForEach(todos) { todo in
                VStack(alignment: .leading) {
                    Text(todo.title).font(.headline)
                    Text(todo.description).font(.caption)
                }
                .onTapGesture {
                    todo.isCompleted.toggle()
                    try? modelContext.save()
                }
            }
            .onDelete { indices in
                for index in indices {
                    modelContext.delete(todos[index])
                }
                try? modelContext.save()
            }
        }
    }
}

// App Configuration
@main
struct TodoApp: App {
    let container = ModelContainer(
        for: TodoItem.self, TodoList.self,
        inMemory: false
    )

    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .modelContainer(container)
    }
}
```

### Core Data (Legacy Support)

```swift
import CoreData

class DataController {
    let container: NSPersistentContainer

    init(inMemory: Bool = false) {
        container = NSPersistentContainer(name: "AppData")

        if inMemory {
            container.persistentStoreDescriptions.first?.url = URL(fileURLWithPath: "/dev/null")
        }

        container.loadPersistentStores { _, error in
            if let error = error {
                fatalError("Core Data error: \(error)")
            }
        }
    }

    var viewContext: NSManagedObjectContext {
        container.viewContext
    }

    func save() {
        let context = container.viewContext

        if context.hasChanges {
            do {
                try context.save()
            } catch {
                print("Save error: \(error)")
            }
        }
    }
}

// Usage in SwiftUI
struct CoreDataView: View {
    @StateObject private var controller = DataController()
    @FetchRequest(entity: NSEntityDescription.entityForName("User", in: NSManagedObjectContext()), sortDescriptors: [])
    var users: FetchedResults<NSManagedObject>

    var body: some View {
        List(users, id: \.self) { user in
            Text(user.value(forKey: "name") as? String ?? "Unknown")
        }
    }
}
```

### Keychain Storage

```swift
class KeychainManager {
    static let shared = KeychainManager()

    enum KeychainError: Error {
        case itemNotFound
        case duplicateItem
        case invalidItemFormat
        case unexpectedStatus(OSStatus)
    }

    func save(_ value: String, for key: String) throws {
        let data = value.data(using: .utf8)!
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecValueData as String: data
        ]

        SecItemDelete(query as CFDictionary)

        let status = SecItemAdd(query as CFDictionary, nil)
        guard status == errSecSuccess else {
            throw KeychainError.unexpectedStatus(status)
        }
    }

    func retrieve(_ key: String) throws -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecReturnData as String: true
        ]

        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)

        guard status != errSecItemNotFound else { return nil }
        guard status == errSecSuccess else {
            throw KeychainError.unexpectedStatus(status)
        }

        guard let data = result as? Data else {
            throw KeychainError.invalidItemFormat
        }

        return String(data: data, encoding: .utf8)
    }

    func delete(_ key: String) throws {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key
        ]

        let status = SecItemDelete(query as CFDictionary)
        guard status == errSecSuccess || status == errSecItemNotFound else {
            throw KeychainError.unexpectedStatus(status)
        }
    }
}

// Usage
Task {
    try KeychainManager.shared.save("secret_token", for: "auth_token")
    let token = try KeychainManager.shared.retrieve("auth_token")
}
```

### UserDefaults

```swift
@propertyWrapper
struct UserDefault<Value> {
    let key: String
    let defaultValue: Value
    let store: UserDefaults = .standard

    var wrappedValue: Value {
        get { store.object(forKey: key) as? Value ?? defaultValue }
        set { store.set(newValue, forKey: key) }
    }
}

class AppSettings {
    @UserDefault(key: "isDarkMode", defaultValue: false)
    static var isDarkMode: Bool

    @UserDefault(key: "fontSize", defaultValue: 16)
    static var fontSize: Int

    @UserDefault(key: "lastLogin", defaultValue: Date(timeIntervalSince1970: 0))
    static var lastLogin: Date
}

struct SettingsView: View {
    @State private var isDark = AppSettings.isDarkMode

    var body: some View {
        Toggle("Dark Mode", isOn: $isDark)
            .onChange(of: isDark) { newValue in
                AppSettings.isDarkMode = newValue
            }
    }
}
```

---

## Networking

### URLSession with Async/Await

```swift
protocol APIClient {
    func request<T: Decodable>(endpoint: APIEndpoint) async throws -> T
}

enum APIEndpoint {
    case users
    case user(id: String)
    case createUser(name: String)

    var url: URL {
        let baseURL = "https://api.example.com"
        switch self {
        case .users:
            return URL(string: "\(baseURL)/users")!
        case .user(let id):
            return URL(string: "\(baseURL)/users/\(id)")!
        case .createUser:
            return URL(string: "\(baseURL)/users")!
        }
    }

    var method: String {
        switch self {
        case .createUser: return "POST"
        default: return "GET"
        }
    }
}

class DefaultAPIClient: APIClient {
    private let session: URLSession
    private let decoder = JSONDecoder()

    init(session: URLSession = .shared) {
        self.session = session
    }

    func request<T: Decodable>(endpoint: APIEndpoint) async throws -> T {
        var request = URLRequest(url: endpoint.url)
        request.httpMethod = endpoint.method
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let (data, response) = try await session.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw URLError(.badServerResponse)
        }

        guard (200...299).contains(httpResponse.statusCode) else {
            throw URLError(.badServerResponse)
        }

        return try decoder.decode(T.self, from: data)
    }
}
```

### Combine Publishers

```swift
import Combine

class NetworkingService {
    private let session: URLSession

    func fetchUsers() -> AnyPublisher<[User], Error> {
        let url = URL(string: "https://api.example.com/users")!

        return URLSession.shared.dataTaskPublisher(for: url)
            .map(\.data)
            .decode(type: [User].self, decoder: JSONDecoder())
            .receive(on: DispatchQueue.main)
            .eraseToAnyPublisher()
    }
}

struct UsersView: View {
    @StateObject private var service = NetworkingService()
    @State private var users: [User] = []
    @State private var cancellables = Set<AnyCancellable>()

    var body: some View {
        List(users) { user in
            Text(user.name)
        }
        .onAppear {
            service.fetchUsers()
                .sink { completion in
                    if case .failure(let error) = completion {
                        print("Error: \(error)")
                    }
                } receiveValue: { users in
                    self.users = users
                }
                .store(in: &cancellables)
        }
    }
}
```

---

## Architecture Patterns

### MVVM Architecture

```swift
// Model
struct User: Identifiable, Codable {
    let id: String
    let name: String
    let email: String
}

// ViewModel
@Observable
class UsersViewModel {
    var users: [User] = []
    var isLoading = false
    var errorMessage: String?

    private let apiClient: APIClient

    init(apiClient: APIClient) {
        self.apiClient = apiClient
    }

    @MainActor
    func loadUsers() async {
        isLoading = true
        defer { isLoading = false }

        do {
            users = try await apiClient.request(endpoint: .users)
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    @MainActor
    func deleteUser(_ user: User) async {
        users.removeAll { $0.id == user.id }
    }
}

// View
struct UsersView: View {
    @State private var viewModel: UsersViewModel

    init(apiClient: APIClient) {
        _viewModel = State(initialValue: UsersViewModel(apiClient: apiClient))
    }

    var body: some View {
        NavigationStack {
            Group {
                if viewModel.isLoading {
                    ProgressView()
                } else if let error = viewModel.errorMessage {
                    VStack {
                        Text("Error: \(error)")
                        Button("Retry") {
                            Task {
                                await viewModel.loadUsers()
                            }
                        }
                    }
                } else {
                    List {
                        ForEach(viewModel.users) { user in
                            VStack(alignment: .leading) {
                                Text(user.name).font(.headline)
                                Text(user.email).font(.caption)
                            }
                        }
                        .onDelete { indices in
                            for index in indices {
                                Task {
                                    await viewModel.deleteUser(viewModel.users[index])
                                }
                            }
                        }
                    }
                }
            }
            .navigationTitle("Users")
            .onAppear {
                Task {
                    await viewModel.loadUsers()
                }
            }
        }
    }
}
```

### Dependency Injection

```swift
protocol UserRepositoryProtocol {
    func getUsers() async throws -> [User]
    func getUser(id: String) async throws -> User
}

class UserRepository: UserRepositoryProtocol {
    private let apiClient: APIClient

    init(apiClient: APIClient) {
        self.apiClient = apiClient
    }

    func getUsers() async throws -> [User] {
        try await apiClient.request(endpoint: .users)
    }

    func getUser(id: String) async throws -> User {
        try await apiClient.request(endpoint: .user(id: id))
    }
}

class AppContainer {
    static let shared = AppContainer()

    let apiClient: APIClient
    let userRepository: UserRepositoryProtocol

    private init() {
        self.apiClient = DefaultAPIClient()
        self.userRepository = UserRepository(apiClient: apiClient)
    }
}

@main
struct AppMain: App {
    let container = AppContainer.shared

    var body: some Scene {
        WindowGroup {
            UsersView(repository: container.userRepository)
        }
    }
}
```

---

## Performance Optimization

### Instruments Usage

```swift
// Time Profiler example: identify slow code
import os

let logger = OSLog(subsystem: "com.example.app", category: "performance")

@Observable
class PerformanceMonitor {
    func measureTask<T>(_ name: String, block: () throws -> T) rethrows -> T {
        let startTime = CFAbsoluteTimeGetCurrent()
        defer {
            let elapsed = (CFAbsoluteTimeGetCurrent() - startTime) * 1000
            os_log("Task: %s completed in %.2f ms", log: logger, type: .debug, name, elapsed)
        }
        return try block()
    }
}

// Usage
let monitor = PerformanceMonitor()
let result = try monitor.measureTask("DataParsing") {
    try parseHugeDataSet()
}
```

### Lazy Loading

```swift
struct LargeListView: View {
    @State private var items: [Item] = []
    @State private var isLoadingMore = false

    var body: some View {
        List(items) { item in
            VStack(alignment: .leading) {
                Text(item.title)
                if item == items.last {
                    HStack {
                        Spacer()
                        ProgressView()
                        Spacer()
                    }
                    .onAppear {
                        Task {
                            await loadMore()
                        }
                    }
                }
            }
        }
    }

    private func loadMore() async {
        guard !isLoadingMore else { return }
        isLoadingMore = true
        defer { isLoadingMore = false }

        let newItems = try? await fetchMoreItems()
        items.append(contentsOf: newItems ?? [])
    }
}
```

---

## Testing

### XCTest

```swift
import XCTest

class UsersViewModelTests: XCTestCase {
    var sut: UsersViewModel!
    var mockAPIClient: MockAPIClient!

    override func setUp() {
        super.setUp()
        mockAPIClient = MockAPIClient()
        sut = UsersViewModel(apiClient: mockAPIClient)
    }

    @MainActor
    func testLoadUsersSuccess() async {
        let expectedUsers = [User(id: "1", name: "Alice", email: "alice@example.com")]
        mockAPIClient.mockUsers = expectedUsers

        await sut.loadUsers()

        XCTAssertEqual(sut.users, expectedUsers)
        XCTAssertFalse(sut.isLoading)
        XCTAssertNil(sut.errorMessage)
    }

    @MainActor
    func testLoadUsersFailure() async {
        mockAPIClient.mockError = NSError(domain: "test", code: 1)

        await sut.loadUsers()

        XCTAssertTrue(sut.users.isEmpty)
        XCTAssertFalse(sut.isLoading)
        XCTAssertNotNil(sut.errorMessage)
    }
}

class MockAPIClient: APIClient {
    var mockUsers: [User]?
    var mockError: Error?

    func request<T: Decodable>(endpoint: APIEndpoint) async throws -> T {
        if let error = mockError {
            throw error
        }
        return mockUsers as! T
    }
}
```

### XCUITest

```swift
class UITests: XCTestCase {
    let app = XCUIApplication()

    override func setUpWithError() throws {
        continueAfterFailure = false
        app.launch()
    }

    func testUserListDisplay() {
        let table = app.tables.firstMatch
        XCTAssertTrue(table.exists)

        let cells = table.cells
        XCTAssertGreaterThan(cells.count, 0)

        let firstCell = cells.element(boundBy: 0)
        XCTAssertTrue(firstCell.exists)
    }

    func testNavigateToUserDetail() {
        let table = app.tables.firstMatch
        let firstCell = table.cells.element(boundBy: 0)
        firstCell.tap()

        let detailText = app.staticTexts["User Detail"]
        XCTAssertTrue(detailText.exists)
    }
}
```

---

## Accessibility

### VoiceOver Support

```swift
struct AccessibleListView: View {
    let items: [AccessibleItem]

    var body: some View {
        List(items) { item in
            VStack(alignment: .leading, spacing: 8) {
                Text(item.title)
                    .font(.headline)
                    .accessibilityAddCharacterCount(item.title.count)

                Text(item.description)
                    .font(.body)
                    .foregroundColor(.secondary)
            }
            .accessibilityElement(children: .combine)
            .accessibilityLabel("Item: \(item.title)")
            .accessibilityValue(item.description)
            .accessibilityHint("Double tap to view details")
        }
    }
}
```

### Dynamic Type Support

```swift
struct DynamicTypeView: View {
    @Environment(\.sizeCategory) var sizeCategory

    var body: some View {
        VStack(spacing: 16) {
            Text("Title")
                .font(.system(.title, design: .default))

            Text("Body")
                .font(.system(.body, design: .default))

            // Responsive spacing
            let spacing = sizeCategory.isAccessibilityCategory ? 24.0 : 16.0

            Button("Action") { }
                .padding(spacing)
                .font(.system(.headline, design: .default))
        }
        .padding()
    }
}
```

---

## App Extensions

### WidgetKit

```swift
import WidgetKit

struct AppWidget: Widget {
    let kind: String = "AppWidget"

    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: Provider()) { entry in
            AppWidgetEntryView(entry: entry)
        }
        .configurationDisplayName("My Widget")
        .description("Shows app statistics")
        .supportedFamilies([.systemSmall, .systemMedium])
    }
}

struct AppWidgetEntryView: View {
    var entry: SimpleEntry

    var body: some View {
        VStack {
            Text("Widget")
                .font(.headline)
            Text(entry.date, style: .time)
                .font(.caption)
        }
        .padding()
    }
}

struct SimpleEntry: TimelineEntry {
    let date: Date
    let data: String = "Sample"
}

struct Provider: TimelineProvider {
    func placeholder(in context: Context) -> SimpleEntry {
        SimpleEntry(date: Date())
    }

    func getSnapshot(in context: Context, completion: @escaping (SimpleEntry) -> ()) {
        completion(SimpleEntry(date: Date()))
    }

    func getTimeline(in context: Context, completion: @escaping (Timeline<SimpleEntry>) -> ()) {
        let entry = SimpleEntry(date: Date())
        let timeline = Timeline(entries: [entry], policy: .atEnd)
        completion(timeline)
    }
}
```

---

## Push Notifications

### APNs Setup

```swift
import UserNotifications

class NotificationManager {
    static let shared = NotificationManager()

    func requestAuthorization() async -> Bool {
        do {
            return try await UNUserNotificationCenter.current()
                .requestAuthorization(options: [.alert, .sound, .badge])
        } catch {
            print("Notification authorization error: \(error)")
            return false
        }
    }

    func registerForRemoteNotifications() {
        DispatchQueue.main.async {
            UIApplication.shared.registerForRemoteNotifications()
        }
    }

    func handleRemoteNotification(_ userInfo: [AnyHashable: Any]) {
        if let aps = userInfo["aps"] as? [String: Any],
           let alert = aps["alert"] as? String {
            print("Remote notification: \(alert)")
        }
    }
}

// AppDelegate setup
class AppDelegate: NSObject, UIApplicationDelegate {
    func application(_ application: UIApplication,
                     didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]? = nil) -> Bool {

        Task {
            let granted = await NotificationManager.shared.requestAuthorization()
            if granted {
                NotificationManager.shared.registerForRemoteNotifications()
            }
        }

        return true
    }

    func application(_ application: UIApplication,
                     didReceiveRemoteNotification userInfo: [AnyHashable: Any],
                     fetchCompletionHandler completionHandler: @escaping (UIBackgroundFetchResult) -> Void) {
        NotificationManager.shared.handleRemoteNotification(userInfo)
        completionHandler(.newData)
    }
}
```

---

## Privacy & Security

### App Tracking Transparency

```swift
import AppTrackingTransparency
import AdSupport

class ATTManager {
    static let shared = ATTManager()

    func requestTrackingAuthorization() async -> ATTrackingManager.AuthorizationStatus {
        return await ATTrackingManager.requestTrackingAuthorization()
    }

    func getAdvertisingIdentifier() -> String? {
        guard ASIdentifierManager.shared().isAdvertisingTrackingEnabled else {
            return nil
        }
        return ASIdentifierManager.shared().advertisingIdentifier.uuidString
    }
}

struct AppView: View {
    @State private var attStatus: ATTrackingManager.AuthorizationStatus?

    var body: some View {
        VStack {
            Button("Request Tracking") {
                Task {
                    let status = await ATTManager.shared.requestTrackingAuthorization()
                    attStatus = status
                }
            }
            if let status = attStatus {
                Text("Status: \(statusText(status))")
            }
        }
    }

    private func statusText(_ status: ATTrackingManager.AuthorizationStatus) -> String {
        switch status {
        case .authorized: return "Authorized"
        case .denied: return "Denied"
        case .notDetermined: return "Not Determined"
        case .restricted: return "Restricted"
        @unknown default: return "Unknown"
        }
    }
}
```

### Privacy Manifests

```json
{
  "NSPrivacyTracking": false,
  "NSPrivacyTrackingDomains": [],
  "NSPrivacyAccessedAPITypes": [
    {
      "NSPrivacyAccessedAPIType": "NSPrivacyAccessedAPICategoryUserDefaults",
      "NSPrivacyAccessedAPITypeReasons": ["CA92.1"]
    },
    {
      "NSPrivacyAccessedAPIType": "NSPrivacyAccessedAPICategoryFileTimestamp",
      "NSPrivacyAccessedAPITypeReasons": ["C617.1"]
    }
  ]
}
```

---

## App Distribution

### TestFlight Setup

```swift
// For beta testing feedback
class BetaFeedbackManager {
    static let shared = BetaFeedbackManager()

    #if DEBUG
    func showBetaFeedbackPrompt() {
        let alert = UIAlertController(title: "Beta Feedback",
                                     message: "Help us improve the app",
                                     preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "Send Feedback", style: .default) { _ in
            // Implementation
        })
        alert.addAction(UIAlertAction(title: "Cancel", style: .cancel))
    }
    #endif
}
```

### StoreKit 2

```swift
import StoreKit

@Observable
class StoreManager {
    var availableProducts: [Product] = []
    var purchasedProductIDs: Set<String> = []

    init() {
        Task {
            await loadProducts()
        }
    }

    @MainActor
    func loadProducts() async {
        do {
            availableProducts = try await Product.products(for: ["com.example.premium"])
        } catch {
            print("Failed to fetch products: \(error)")
        }
    }

    @MainActor
    func purchase(_ product: Product) async {
        do {
            let result = try await product.purchase()

            switch result {
            case .success(.verified(let transaction)):
                purchasedProductIDs.insert(product.id)
                await transaction.finish()
            case .userCancelled, .pending:
                break
            @unknown default:
                break
            }
        } catch {
            print("Purchase failed: \(error)")
        }
    }
}
```

---

## Production Checklist

- [ ] Implement proper error handling and user feedback
- [ ] Use async/await for all async operations
- [ ] Test on multiple device sizes and iOS versions
- [ ] Implement accessibility (VoiceOver, Dynamic Type)
- [ ] Secure sensitive data in Keychain
- [ ] Add push notification support
- [ ] Implement proper logging and analytics
- [ ] Test performance with Instruments
- [ ] Create comprehensive unit and UI tests
- [ ] Set up privacy manifest
- [ ] Prepare for App Store submission
- [ ] Configure TestFlight for beta testing

---

## References

- [Apple Developer Documentation](https://developer.apple.com/documentation/)
- [SwiftUI Documentation](https://developer.apple.com/documentation/swiftui)
- [Concurrency Documentation](https://developer.apple.com/documentation/swift/concurrency)
- [SwiftData Documentation](https://developer.apple.com/documentation/swiftdata)
- [StoreKit 2 Documentation](https://developer.apple.com/documentation/storekit)
