# Mobile App Testing Reference Guide

A comprehensive guide to testing strategies, tools, and best practices for iOS, Android, React Native, and Flutter applications.

## Table of Contents
1. [Testing Pyramid](#testing-pyramid)
2. [Unit Testing](#unit-testing)
3. [Widget/Component Testing](#widgetcomponent-testing)
4. [Integration Testing](#integration-testing)
5. [E2E/UI Testing](#e2eui-testing)
6. [Snapshot & Visual Regression](#snapshot--visual-regression)
7. [Performance Testing](#performance-testing)
8. [Accessibility Testing](#accessibility-testing)
9. [Security Testing](#security-testing)
10. [Device Farms](#device-farms)
11. [CI/CD Integration](#cicd-integration)
12. [Crash Reporting](#crash-reporting)
13. [TDD & BDD Patterns](#tdd--bdd-patterns)

---

## Testing Pyramid

The mobile testing pyramid follows the 70/20/10 ratio:

```
      E2E Tests (10%)
        UI Testing
           |
    Integration Tests (20%)
       API, Database
            |
      Unit Tests (70%)
    Business Logic
```

**Rationale:**
- **70% Unit Tests**: Fast, isolated, cheap to maintain. Test business logic, calculations, and algorithms
- **20% Integration Tests**: Test interactions between components, API calls, database operations
- **10% E2E/UI Tests**: Test critical user journeys end-to-end. Slow and flaky, use sparingly

---

## Unit Testing

### iOS: XCTest

```swift
import XCTest
@testable import MyApp

class LoginViewModelTests: XCTestCase {
    var viewModel: LoginViewModel!

    override func setUp() {
        super.setUp()
        viewModel = LoginViewModel()
    }

    func testEmailValidation_validEmail_shouldPass() {
        // Arrange
        let validEmail = "test@example.com"

        // Act
        let isValid = viewModel.isValidEmail(validEmail)

        // Assert
        XCTAssertTrue(isValid)
    }

    func testEmailValidation_invalidEmail_shouldFail() {
        let invalidEmail = "notanemail"
        XCTAssertFalse(viewModel.isValidEmail(invalidEmail))
    }

    func testLogin_withValidCredentials_callsCompletion() {
        let expectation = self.expectation(description: "Login completion")
        var loginSuccess = false

        viewModel.login(email: "test@test.com", password: "secure123") { success in
            loginSuccess = success
            expectation.fulfill()
        }

        waitForExpectations(timeout: 5.0)
        XCTAssertTrue(loginSuccess)
    }
}
```

### Android: JUnit + MockK

```kotlin
import org.junit.Test
import org.junit.Before
import io.mockk.*
import com.example.app.viewmodel.LoginViewModel
import com.example.app.repository.AuthRepository

class LoginViewModelTest {
    private lateinit var viewModel: LoginViewModel
    private val authRepository: AuthRepository = mockk()

    @Before
    fun setUp() {
        viewModel = LoginViewModel(authRepository)
    }

    @Test
    fun testEmailValidation_validEmail_shouldPass() {
        // Arrange & Act
        val isValid = viewModel.isValidEmail("test@example.com")

        // Assert
        assert(isValid)
    }

    @Test
    fun testLogin_withValidCredentials_shouldReturnSuccess() {
        // Arrange
        val email = "test@test.com"
        val password = "secure123"
        coEvery { authRepository.login(email, password) } returns Result.success(Unit)

        // Act
        val result = runBlocking { viewModel.login(email, password) }

        // Assert
        assert(result.isSuccess)
        coVerify { authRepository.login(email, password) }
    }

    @Test
    fun testLogin_withInvalidEmail_shouldReturnError() {
        // Act
        val result = viewModel.validateEmail("notanemail")

        // Assert
        assert(result.isFailure)
    }
}
```

### React Native: Jest

```javascript
import { LoginViewModel } from '../viewmodels/LoginViewModel';
import { AuthService } from '../services/AuthService';

jest.mock('../services/AuthService');

describe('LoginViewModel', () => {
  let viewModel;

  beforeEach(() => {
    viewModel = new LoginViewModel();
    jest.clearAllMocks();
  });

  test('isValidEmail returns true for valid email', () => {
    // Arrange & Act
    const result = viewModel.isValidEmail('test@example.com');

    // Assert
    expect(result).toBe(true);
  });

  test('isValidEmail returns false for invalid email', () => {
    expect(viewModel.isValidEmail('notanemail')).toBe(false);
  });

  test('login with valid credentials calls AuthService', async () => {
    // Arrange
    AuthService.login.mockResolvedValue({ token: 'abc123' });

    // Act
    const result = await viewModel.login('test@test.com', 'secure123');

    // Assert
    expect(AuthService.login).toHaveBeenCalledWith('test@test.com', 'secure123');
    expect(result.token).toBe('abc123');
  });
});
```

### Flutter: flutter_test

```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:my_app/viewmodels/login_viewmodel.dart';
import 'package:mockito/mockito.dart';

class MockAuthRepository extends Mock implements AuthRepository {}

void main() {
  group('LoginViewModel', () {
    late LoginViewModel viewModel;
    late MockAuthRepository mockAuthRepository;

    setUp(() {
      mockAuthRepository = MockAuthRepository();
      viewModel = LoginViewModel(mockAuthRepository);
    });

    test('isValidEmail returns true for valid email', () {
      // Arrange & Act
      final result = viewModel.isValidEmail('test@example.com');

      // Assert
      expect(result, true);
    });

    test('login with valid credentials returns success', () async {
      // Arrange
      when(mockAuthRepository.login('test@test.com', 'secure123'))
          .thenAnswer((_) async => AuthToken('abc123'));

      // Act
      final result = await viewModel.login('test@test.com', 'secure123');

      // Assert
      expect(result.token, 'abc123');
      verify(mockAuthRepository.login('test@test.com', 'secure123')).called(1);
    });
  });
}
```

---

## Widget/Component Testing

### iOS: SwiftUI Previews Testing

```swift
import SwiftUI

struct LoginView_Previews: PreviewProvider {
    static var previews: some View {
        Group {
            LoginView(viewModel: LoginViewModel())
                .preferredColorScheme(.light)
                .previewDisplayName("Light Mode")

            LoginView(viewModel: LoginViewModel())
                .preferredColorScheme(.dark)
                .previewDisplayName("Dark Mode")

            LoginView(viewModel: LoginViewModel(isLoading: true))
                .previewDisplayName("Loading State")
        }
    }
}

class LoginViewTests: XCTestCase {
    func testLoginViewRenders() throws {
        let viewModel = LoginViewModel()
        let loginView = LoginView(viewModel: viewModel)

        // Test that view hierarchy renders without crashing
        let controller = UIHostingController(rootView: loginView)
        let window = UIWindow(frame: UIScreen.main.bounds)
        window.rootViewController = controller
        window.makeKeyAndVisible()

        XCTAssertNotNil(controller.view)
    }
}
```

### Android: Compose Testing

```kotlin
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createComposeRule
import org.junit.Rule
import org.junit.Test
import com.example.app.ui.LoginScreen

class LoginScreenTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun testLoginButton_isDisplayed() {
        composeTestRule.setContent {
            LoginScreen()
        }

        composeTestRule
            .onNodeWithText("Login")
            .assertIsDisplayed()
    }

    @Test
    fun testEmailField_acceptsInput() {
        composeTestRule.setContent {
            LoginScreen()
        }

        composeTestRule
            .onNodeWithTag("emailField")
            .performTextInput("test@example.com")
            .assertTextEquals("test@example.com")
    }

    @Test
    fun testLoginFlow() {
        composeTestRule.setContent {
            LoginScreen()
        }

        // Enter email
        composeTestRule
            .onNodeWithTag("emailField")
            .performTextInput("test@test.com")

        // Enter password
        composeTestRule
            .onNodeWithTag("passwordField")
            .performTextInput("secure123")

        // Click login button
        composeTestRule
            .onNodeWithText("Login")
            .performClick()

        // Verify loading state
        composeTestRule
            .onNodeWithTag("loadingIndicator")
            .assertIsDisplayed()
    }
}
```

### React Native: React Testing Library

```javascript
import { render, screen, fireEvent } from '@testing-library/react-native';
import LoginScreen from '../screens/LoginScreen';

describe('LoginScreen', () => {
  test('renders login form', () => {
    render(<LoginScreen />);

    expect(screen.getByPlaceholderText('Email')).toBeTruthy();
    expect(screen.getByPlaceholderText('Password')).toBeTruthy();
    expect(screen.getByText('Login')).toBeTruthy();
  });

  test('updates email input on change', () => {
    render(<LoginScreen />);

    const emailInput = screen.getByPlaceholderText('Email');
    fireEvent.changeText(emailInput, 'test@example.com');

    expect(emailInput.props.value).toBe('test@example.com');
  });

  test('calls login handler on button press', () => {
    const mockLogin = jest.fn();
    render(<LoginScreen onLogin={mockLogin} />);

    fireEvent.press(screen.getByText('Login'));

    expect(mockLogin).toHaveBeenCalled();
  });
});
```

---

## Integration Testing

### API Mocking with Interceptors

```swift
// iOS: Network mocking with URLProtocol
class MockURLProtocol: URLProtocol {
    static var mockResponses = [URL: (response: URLResponse, data: Data)]()

    override class func canInit(with request: URLRequest) -> Bool {
        return true
    }

    override class func canonicalRequest(for request: URLRequest) -> URLRequest {
        return request
    }

    override func startLoading() {
        guard let url = request.url,
              let (response, data) = Self.mockResponses[url] else {
            let error = NSError(domain: "MockError", code: 0)
            client?.urlProtocol(self, didFailWithError: error)
            return
        }

        client?.urlProtocol(self, didReceive: response, cacheStoragePolicy: .notAllowed)
        client?.urlProtocol(self, didLoad: data)
        client?.urlProtocolDidFinishLoading(self)
    }

    override func stopLoading() {}
}

class APIIntegrationTests: XCTestCase {
    override func setUp() {
        super.setUp()

        let userData = try! JSONEncoder().encode(User(id: 1, name: "John"))
        let response = HTTPURLResponse(url: URL(string: "https://api.example.com/user")!,
                                      statusCode: 200, httpVersion: nil, headerFields: nil)!
        MockURLProtocol.mockResponses[URL(string: "https://api.example.com/user")!] = (response, userData)
    }

    func testFetchUser() async throws {
        let user = try await APIClient.shared.fetchUser(id: 1)
        XCTAssertEqual(user.name, "John")
    }
}
```

```kotlin
// Android: API mocking with MockWebServer
class APIIntegrationTest {
    @get:Rule
    val instantExecutorRule = InstantTaskExecutorRule()

    private val mockWebServer = MockWebServer()
    private lateinit var apiService: APIService

    @Before
    fun setUp() {
        mockWebServer.start()
        apiService = Retrofit.Builder()
            .baseUrl(mockWebServer.url("/"))
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(APIService::class.java)
    }

    @After
    fun tearDown() {
        mockWebServer.shutdown()
    }

    @Test
    fun testFetchUser() = runBlocking {
        // Arrange
        mockWebServer.enqueue(MockResponse().setBody("""
            {"id": 1, "name": "John"}
        """))

        // Act
        val user = apiService.getUser(1)

        // Assert
        assert(user.name == "John")
    }
}
```

### Database Testing

```swift
// iOS: Core Data testing
class CoreDataTests: XCTestCase {
    var context: NSManagedObjectContext!

    override func setUp() {
        super.setUp()
        let container = NSPersistentContainer(name: "TestModel")
        container.persistentStoreDescriptions.first?.url = URL(fileURLWithPath: "/dev/null")

        container.loadPersistentStores { _, error in
            if let error = error as NSError? {
                fatalError("Loading store error: \(error)")
            }
        }
        context = container.viewContext
    }

    func testSaveUser() throws {
        let user = UserEntity(context: context)
        user.id = 1
        user.name = "John"

        try context.save()

        let fetchRequest: NSFetchRequest<UserEntity> = UserEntity.fetchRequest()
        let results = try context.fetch(fetchRequest)

        XCTAssertEqual(results.first?.name, "John")
    }
}
```

```kotlin
// Android: Room database testing
@RunWith(AndroidTestRunner::class)
class UserDaoTest {
    @get:Rule
    val instantExecutorRule = InstantTaskExecutorRule()

    private lateinit var database: AppDatabase
    private lateinit var userDao: UserDao

    @Before
    fun setup() {
        database = Room.inMemoryDatabaseBuilder(
            ApplicationProvider.getApplicationContext(),
            AppDatabase::class.java
        ).build()
        userDao = database.userDao()
    }

    @After
    fun closeDb() {
        database.close()
    }

    @Test
    fun insertAndReadUser() = runBlocking {
        val user = User(id = 1, name = "John")
        userDao.insert(user)

        val loaded = userDao.getUser(1)
        assert(loaded.name == "John")
    }
}
```

---

## E2E/UI Testing

### iOS: XCUITest

```swift
import XCTest

class LoginE2ETests: XCTestCase {
    let app = XCUIApplication()

    override func setUp() {
        super.setUp()
        continueAfterFailure = false
        app.launch()
    }

    func testCompleteLoginFlow() {
        let emailField = app.textFields["Email"]
        let passwordField = app.secureTextFields["Password"]
        let loginButton = app.buttons["Login"]

        emailField.tap()
        emailField.typeText("test@example.com")

        passwordField.tap()
        passwordField.typeText("secure123")

        loginButton.tap()

        let dashboard = app.staticTexts["Dashboard"]
        XCTAssertTrue(dashboard.waitForExistence(timeout: 5.0))
    }

    func testErrorHandling() {
        let emailField = app.textFields["Email"]
        let loginButton = app.buttons["Login"]

        emailField.tap()
        emailField.typeText("invalid-email")
        loginButton.tap()

        let errorAlert = app.alerts["Login Error"]
        XCTAssertTrue(errorAlert.waitForExistence(timeout: 3.0))
    }
}
```

### Android: Espresso

```kotlin
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.action.ViewActions.click
import androidx.test.espresso.action.ViewActions.typeText
import androidx.test.espresso.assertion.ViewAssertions.matches
import androidx.test.espresso.matcher.ViewMatchers.*
import androidx.test.ext.junit.rules.ActivityScenarioRule
import org.junit.Rule

class LoginE2ETest {
    @get:Rule
    val activityRule = ActivityScenarioRule(LoginActivity::class.java)

    @Test
    fun testCompleteLoginFlow() {
        onView(withId(R.id.emailField))
            .perform(typeText("test@example.com"))

        onView(withId(R.id.passwordField))
            .perform(typeText("secure123"))

        onView(withId(R.id.loginButton))
            .perform(click())

        onView(withId(R.id.dashboard))
            .check(matches(isDisplayed()))
    }

    @Test
    fun testInvalidEmailError() {
        onView(withId(R.id.emailField))
            .perform(typeText("invalid"))

        onView(withId(R.id.loginButton))
            .perform(click())

        onView(withText("Invalid email"))
            .check(matches(isDisplayed()))
    }
}
```

### React Native: Detox

```javascript
describe('Login Flow', () => {
  beforeAll(async () => {
    await device.launchApp();
  });

  beforeEach(async () => {
    await device.reloadReactNative();
  });

  it('should login with valid credentials', async () => {
    await element(by.id('emailInput')).typeText('test@example.com');
    await element(by.id('passwordInput')).typeText('secure123');
    await element(by.text('Login')).multiTap();

    await waitFor(element(by.id('dashboardScreen')))
      .toBeVisible()
      .withTimeout(5000);
  });

  it('should show error for invalid email', async () => {
    await element(by.id('emailInput')).typeText('invalid');
    await element(by.text('Login')).tap();

    await expect(element(by.text('Invalid email'))).toBeVisible();
  });
});
```

### Mobile: Maestro (YAML Flows)

```yaml
appId: com.example.myapp
---
- launchApp
- tapOn:
    id: "loginButton"
- inputText: "test@example.com"
- tapOn:
    id: "passwordField"
- inputText: "secure123"
- tapOn:
    text: "Login"
- assertVisible:
    id: "dashboardScreen"
- takeScreenshot: "login_success"
```

### Appium

```python
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestLogin:
    def setup_method(self):
        caps = {
            'platformName': 'Android',
            'deviceName': 'emulator-5554',
            'app': '/path/to/app.apk',
            'automationName': 'UiAutomator2'
        }
        self.driver = webdriver.Remote('http://localhost:4723/wd/hub', caps)

    def test_login_flow(self):
        email_field = self.driver.find_element(AppiumBy.ID, 'com.example:id/emailField')
        password_field = self.driver.find_element(AppiumBy.ID, 'com.example:id/passwordField')
        login_button = self.driver.find_element(AppiumBy.ID, 'com.example:id/loginButton')

        email_field.send_keys('test@example.com')
        password_field.send_keys('secure123')
        login_button.click()

        wait = WebDriverWait(self.driver, 10)
        dashboard = wait.until(
            EC.presence_of_element_located((AppiumBy.ID, 'com.example:id/dashboard'))
        )
        assert dashboard.is_displayed()
```

---

## Snapshot & Visual Regression

### iOS: Snapshot Testing with iOSSnapshotTestCase

```swift
import FBSnapshotTestCase

class LoginViewSnapshotTests: FBSnapshotTestCase {
    override func setUp() {
        super.setUp()
        recordMode = false
    }

    func testLoginViewLight() {
        let viewModel = LoginViewModel()
        let view = LoginView(viewModel: viewModel)

        FBSnapshotVerifyView(view)
    }

    func testLoginViewDark() {
        let viewModel = LoginViewModel()
        let view = LoginView(viewModel: viewModel)
            .preferredColorScheme(.dark)

        FBSnapshotVerifyView(view)
    }

    func testLoginViewLoadingState() {
        let viewModel = LoginViewModel(isLoading: true)
        let view = LoginView(viewModel: viewModel)

        FBSnapshotVerifyView(view)
    }
}
```

### Percy Integration

```swift
// iOS: Percy screenshot integration
import PercyOCR

class PercyTests: XCTestCase {
    let percy = PercyOCR()

    func testLoginScreen() {
        // Setup and navigate to login screen
        let app = XCUIApplication()
        app.launch()

        // Take Percy screenshot
        percy.screenshot(name: "login_screen")
    }

    func testDarkModeLogin() {
        // Setup dark mode
        // ...
        percy.screenshot(name: "login_screen_dark")
    }
}
```

### Applitools Eyes Integration

```kotlin
// Android: Applitools Eyes
import com.applitools.eyes.android.Eyes
import com.applitools.eyes.BatchInfo
import com.applitools.eyes.RectangleSize

class VisualRegressionTest {
    private val eyes = Eyes()

    @Before
    fun setUp() {
        eyes.apiKey = "YOUR_APPLITOOLS_API_KEY"
        eyes.batch = BatchInfo("Mobile App Tests")
    }

    @Test
    fun testLoginScreenVisuals() {
        eyes.open("MyApp", "Login Screen", RectangleSize(375, 812))

        // Navigate to login screen
        // ...

        eyes.checkWindow("Login Form")

        eyes.close()
    }
}
```

---

## Performance Testing

### Memory Profiling

```swift
// iOS: Memory profiling with Instruments
import os

class MemoryProfiler {
    func measureMemoryUsage(operation: () -> Void) {
        let before = os_proc_available_memory()
        operation()
        let after = os_proc_available_memory()
        let used = (before - after) / (1024 * 1024)
        print("Memory used: \(used) MB")
    }
}

class PerformanceTests: XCTestCase {
    func testMemoryUsageDuringListScroll() {
        let measure = XCTestMetric()
        measure.value = NSNumber(value: 1)

        self.measure(metrics: [XCTMemoryMetric()]) {
            // Scroll through list
        }
    }
}
```

```kotlin
// Android: Battery and memory testing
class PerformanceTest {
    @get:Rule
    val perfettoRule = PerfettoHelper.benchmarkRule()

    @Test
    fun testBatteryUsageDuringLongOperation() = benchmarkRule.measureRepeated {
        // Your operation here
        runBlocking {
            delay(5000)
        }
    }

    fun checkMemoryUsage() {
        val runtime = Runtime.getRuntime()
        val usedMemory = runtime.totalMemory() - runtime.freeMemory()
        val usedMemoryMB = usedMemory / (1024 * 1024)
        println("Used memory: $usedMemoryMB MB")
    }
}
```

### Load Testing

```javascript
// React Native: Load testing with Artillery
const artillery = require('artillery');

describe('Load Testing', () => {
  it('should handle 100 concurrent users', async () => {
    const config = {
      target: 'https://api.example.com',
      phases: [
        { duration: 60, arrivalRate: 10 }
      ]
    };

    // Run load test
    const result = await artillery.run(config);
    expect(result.succeeded).toBe(true);
  });
});
```

---

## Accessibility Testing

### iOS: Accessibility Inspector

```swift
class AccessibilityTests: XCTestCase {
    func testLoginViewAccessibility() {
        let app = XCUIApplication()
        app.launch()

        // Check element labels
        let emailField = app.textFields["Email"]
        XCTAssertTrue(emailField.label.count > 0)

        // Check hints
        XCTAssertTrue(emailField.value is String)

        // Verify focus order
        let emailField = app.textFields.element(boundBy: 0)
        let passwordField = app.secureTextFields.element(boundBy: 0)
        let loginButton = app.buttons.element(boundBy: 0)

        // Tab through elements
        emailField.tap()
        XCTAssertTrue(emailField.hasFocus)
    }

    func testTalkBackCompatibility() {
        let app = XCUIApplication()
        app.launch()

        // Enable accessibility features
        let settings = app.staticTexts["Settings"]
        settings.tap()

        // Verify VoiceOver compatibility
    }
}
```

### Android: Accessibility Testing

```kotlin
import androidx.test.espresso.accessibility.AccessibilityChecks

class AccessibilityTest {
    @get:Rule
    val activityRule = ActivityScenarioRule(LoginActivity::class.java)

    init {
        // Enable accessibility checks
        AccessibilityChecks.enable()
    }

    @Test
    fun testLoginScreenAccessibility() {
        onView(withId(R.id.emailField))
            .check(matches(hasContentDescription()))

        onView(withId(R.id.passwordField))
            .check(matches(hasContentDescription()))
    }

    @Test
    fun testTalkBackNavigation() {
        // Test screen reader navigation
        onView(withId(R.id.emailField)).perform(click())
        onView(isRoot()).perform(pressKey(KeyEvent.KEYCODE_DPAD_DOWN))
    }
}
```

### Flutter: Accessibility

```dart
testWidgets('Login screen is accessible', (WidgetTester tester) async {
  await tester.pumpWidget(const MyApp());

  // Verify semantic labels
  expect(find.bySemanticsLabel('Email'), findsOneWidget);
  expect(find.bySemanticsLabel('Password'), findsOneWidget);

  // Test with SemanticsHandle
  final SemanticsHandle handle = tester.ensureSemantics();
  expect(handle.handleLayer.semanticsLayer, isNotNull);
  handle.dispose();
});
```

---

## Security Testing

### Static Analysis & OWASP Checks

```bash
# iOS: Using SwiftLint for security
swiftlint analyze --path Sources/

# Android: Using Android Lint for security issues
./gradlew lint

# React Native: Using ESLint security plugin
npm install eslint-plugin-security
eslint --ext .js,.jsx .
```

```kotlin
// Android: Certificate pinning test
@Test
fun testCertificatePinning() {
    val certificatePinner = CertificatePinner.Builder()
        .add("api.example.com", "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
        .build()

    val client = OkHttpClient.Builder()
        .certificatePinner(certificatePinner)
        .build()

    // Verify pinning is enabled
}
```

```swift
// iOS: Secure storage testing
class SecureStorageTests: XCTestCase {
    func testKeychainStorage() {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: "userPassword",
            kSecValueData as String: "secret123".data(using: .utf8)!
        ]

        SecItemAdd(query as CFDictionary, nil)

        // Verify it's stored securely
        var result: AnyObject?
        SecItemCopyMatching(query as CFDictionary, &result)
        XCTAssertNotNil(result)
    }
}
```

---

## Device Farms

### BrowserStack

```yaml
# BrowserStack configuration
capabilities:
  - browserstack.user: YOUR_USERNAME
    browserstack.key: YOUR_ACCESS_KEY
    app: bs://APP_ID
    device: iPhone 14 Pro Max
    os_version: "16"
    real_mobile: true
    build: "Build 1"
```

### Firebase Test Lab

```bash
# Deploy and test on Firebase Test Lab
gcloud firebase test android run \
  --app=path/to/app.apk \
  --test=path/to/test.apk \
  --device model=Pixel6,version=31,locale=en,orientation=portrait
```

### AWS Device Farm

```python
import boto3

client = boto3.client('devicefarm')

response = client.create_run(
    projectArn='arn:aws:devicefarm:us-west-2:123456789012:project:PROJECT_ARN',
    appArn='arn:aws:devicefarm:us-west-2:123456789012:app:APP_ARN',
    devicePoolArn='arn:aws:devicefarm:us-west-2:123456789012:devicepool:POOL_ARN',
    test={
        'type': 'APPIUM_JAVA_TESTNG',
        'testPackageArn': 'arn:aws:devicefarm:...'
    }
)
```

---

## CI/CD Integration

### GitHub Actions for iOS

```yaml
name: iOS Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3

      - name: Select Xcode
        run: sudo xcode-select -s /Applications/Xcode.app/Contents/Developer

      - name: Install dependencies
        run: pod install

      - name: Run unit tests
        run: xcodebuild test -scheme MyApp -destination 'generic/platform=iOS'

      - name: Run UI tests
        run: xcodebuild test -scheme MyAppUITests -destination 'generic/platform=iOS'

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### GitHub Actions for Android

```yaml
name: Android Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up JDK
        uses: actions/setup-java@v3
        with:
          java-version: '11'

      - name: Run unit tests
        run: ./gradlew testDebugUnitTest

      - name: Run instrumented tests
        uses: reactivecircus/android-emulator-runner@v2
        with:
          api-level: 31
          script: ./gradlew connectedAndroidTest

      - name: Upload reports
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: test-reports
          path: app/build/reports
```

### GitHub Actions for React Native

```yaml
name: React Native Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm ci

      - name: Run unit tests
        run: npm run test:unit

      - name: Run E2E tests
        run: npm run test:e2e

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Crash Reporting

### Crashlytics Setup

```swift
// iOS: Firebase Crashlytics
import Firebase

func application(_ application: UIApplication,
                 didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
    FirebaseApp.configure()

    // Test crash reporting
    #if DEBUG
    // Only log in production
    #else
    Crashlytics.crashlytics().setCrashlyticsCollectionEnabled(true)
    #endif

    return true
}

// Log custom errors
Crashlytics.crashlytics().record(error: NSError(domain: "com.example.app", code: -1))
```

```kotlin
// Android: Firebase Crashlytics
import com.google.firebase.crashlytics.FirebaseCrashlytics

class MyApp : Application() {
    override fun onCreate() {
        super.onCreate()

        // Enable Crashlytics collection
        FirebaseCrashlytics.getInstance().setCrashlyticsCollectionEnabled(!BuildConfig.DEBUG)
    }
}

// Log custom errors
FirebaseCrashlytics.getInstance().recordException(Exception("Custom error"))
```

### Sentry Integration

```javascript
// React Native: Sentry setup
import * as Sentry from "@sentry/react-native";

Sentry.init({
  dsn: "https://YOUR_KEY@sentry.io/YOUR_PROJECT_ID",
  tracesSampleRate: 1.0,
  enableAutoSessionTracking: true
});

// Capture errors
try {
  // Code that might fail
} catch (error) {
  Sentry.captureException(error);
}
```

### Bugsnag Comparison

```
| Feature        | Crashlytics | Sentry | Bugsnag |
|----------------|-------------|--------|---------|
| Real-time Alerts | Yes        | Yes    | Yes     |
| Session Tracking | Yes        | Yes    | Yes     |
| Custom Events  | Yes        | Yes    | Yes     |
| Source Maps    | Yes        | Yes    | Yes     |
| Free Tier      | Generous   | Limited| Moderate|
| Self-hosted    | No         | Yes    | No      |
```

---

## TDD & BDD Patterns

### TDD Cycle: Red-Green-Refactor

```swift
// RED: Write failing test
func testAddition_withPositiveNumbers_shouldReturnSum() {
    let calculator = Calculator()
    let result = calculator.add(2, 3)
    XCTAssertEqual(result, 5) // FAIL
}

// GREEN: Write minimal code to pass
class Calculator {
    func add(_ a: Int, _ b: Int) -> Int {
        return a + b
    }
}

// REFACTOR: Improve code quality
class Calculator {
    func add(_ numbers: Int...) -> Int {
        return numbers.reduce(0, +)
    }
}
```

### BDD with Cucumber/Gherkin

```gherkin
Feature: User Login
  Scenario: Successful login with valid credentials
    Given user is on the login screen
    When user enters email "test@example.com"
    And user enters password "secure123"
    And user taps login button
    Then user is navigated to dashboard
    And welcome message is displayed

  Scenario: Failed login with invalid email
    Given user is on the login screen
    When user enters email "invalid"
    And user taps login button
    Then error message "Invalid email" is displayed
```

```swift
// iOS: Step definitions
import Gherkin

final class LoginSteps {
    var app: XCUIApplication!

    @Given("user is on the login screen")
    func userOnLoginScreen() {
        app = XCUIApplication()
        app.launch()
    }

    @When("user enters email {}")
    func userEntersEmail(_ email: String) {
        app.textFields["Email"].typeText(email)
    }

    @Then("user is navigated to {}")
    func userNavigatedTo(_ screen: String) {
        XCTAssert(app.staticTexts[screen].exists)
    }
}
```

---

## Best Practices Summary

1. **Maintain the Testing Pyramid**: 70% unit, 20% integration, 10% E2E
2. **Keep Tests Independent**: Each test should run in isolation
3. **Use Descriptive Names**: Test names should explain what is being tested
4. **Mock External Dependencies**: Never hit real APIs in tests
5. **Test User Behavior**: Focus on what users do, not implementation details
6. **Automate Everything**: Integrate tests into CI/CD pipeline
7. **Monitor Crash Reports**: Use crash reporting tools to catch production issues
8. **Measure Performance**: Profile memory, battery, and network usage
9. **Prioritize Accessibility**: Test with screen readers and accessibility tools
10. **Security First**: Include security testing in your pipeline

---

**Last Updated**: March 2026
**Version**: 1.0
