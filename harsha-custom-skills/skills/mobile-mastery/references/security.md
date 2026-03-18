# Mobile Security Reference Guide

Comprehensive guide covering iOS (Swift) and Android (Kotlin) security best practices, OWASP Mobile Top 10, and production-ready implementations.

## Table of Contents

- [1. OWASP Mobile Top 10 (2024)](#1-owasp-mobile-top-10-2024)
- [2. Secure Data Storage](#2-secure-data-storage)
- [3. Cryptography Implementation](#3-cryptography-implementation)
- [4. Secure WebView Implementation](#4-secure-webview-implementation)
- [5. Secure Deep Link Validation](#5-secure-deep-link-validation)
- [6. RASP (Runtime Application Self-Protection)](#6-rasp-runtime-application-self-protection)
- [7. Binary Protections](#7-binary-protections)
- [8. Privacy Compliance](#8-privacy-compliance)

---

## 1. OWASP Mobile Top 10 (2024)

### M1: Improper Credential Usage
**Vulnerability**: Exposing API credentials, tokens, or keys in code or insecure storage.

**iOS Mitigation**:
```swift
import Security

class CredentialManager {
    static let shared = CredentialManager()

    func storeCredential(_ credential: String, forKey key: String) throws {
        let data = credential.data(using: .utf8)!
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecValueData as String: data,
            kSecAttrAccessible as String: kSecAttrAccessibleWhenUnlockedThisDeviceOnly
        ]

        SecItemDelete(query as CFDictionary)
        let status = SecItemAdd(query as CFDictionary, nil)
        guard status == errSecSuccess else { throw KeychainError.storeFailed }
    }

    func retrieveCredential(forKey key: String) throws -> String {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecReturnData as String: true
        ]

        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)
        guard status == errSecSuccess,
              let data = result as? Data,
              let credential = String(data: data, encoding: .utf8)
        else { throw KeychainError.retrieveFailed }

        return credential
    }
}

enum KeychainError: Error {
    case storeFailed
    case retrieveFailed
}
```

**Android Mitigation**:
```kotlin
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

class CredentialManager(context: Context) {
    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()

    private val encryptedSharedPrefs = EncryptedSharedPreferences.create(
        context,
        "secret_shared_prefs",
        masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )

    fun storeCredential(key: String, value: String) {
        encryptedSharedPrefs.edit().putString(key, value).apply()
    }

    fun retrieveCredential(key: String): String? {
        return encryptedSharedPrefs.getString(key, null)
    }
}
```

### M2: Inadequate Supply Chain Security
**Vulnerability**: Vulnerable dependencies, compromised libraries, or untrusted sources.

**Mitigation**: Use dependency scanning, SBOM (Software Bill of Materials), and pin dependency versions.

```kotlin
// Android: gradle build
dependencies {
    // Use specific versions, avoid dynamic versions
    implementation("com.squareup.okhttp3:okhttp:4.11.0") // Good
    // implementation("com.squareup.okhttp3:okhttp:4.+") // Bad
}

// Use dependency verification
dependencyVerification {
    verify(
        "com.squareup.okhttp3:okhttp:4.11.0",
        "sha256:abc123..."
    )
}
```

### M3: Insecure Authentication
**Vulnerability**: Weak password policies, biometric bypass, or session management issues.

**iOS Biometric Authentication**:
```swift
import LocalAuthentication

class BiometricAuth {
    func authenticateWithBiometrics(completion: @escaping (Bool, Error?) -> Void) {
        let context = LAContext()
        var error: NSError?

        guard context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error) else {
            completion(false, error)
            return
        }

        context.evaluatePolicy(
            .deviceOwnerAuthenticationWithBiometrics,
            localizedReason: "Authenticate to access your account"
        ) { success, error in
            DispatchQueue.main.async {
                completion(success, error)
            }
        }
    }
}
```

**Android Biometric Authentication**:
```kotlin
import androidx.biometric.BiometricPrompt
import androidx.biometric.BiometricPrompt.PromptInfo

class BiometricAuthManager(activity: FragmentActivity) {
    private val biometricPrompt = BiometricPrompt(
        activity,
        object : BiometricPrompt.AuthenticationCallback() {
            override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
                super.onAuthenticationSucceeded(result)
                // Authentication successful
            }

            override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                super.onAuthenticationError(errorCode, errString)
                // Handle error
            }
        }
    )

    fun authenticate() {
        val promptInfo = PromptInfo.Builder()
            .setTitle("Biometric Authentication")
            .setNegativeButtonText("Cancel")
            .setAllowedAuthenticators(
                BiometricManager.Authenticators.BIOMETRIC_STRONG
            )
            .build()

        biometricPrompt.authenticate(promptInfo)
    }
}
```

### M4: Insufficient Input Validation
**Vulnerability**: SQL injection, XSS, command injection, or unsafe data processing.

**iOS Input Validation**:
```swift
class InputValidator {
    static func validateEmail(_ email: String) -> Bool {
        let pattern = "^[A-Z0-9a-z._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}$"
        return NSPredicate(format: "SELF MATCHES %@", pattern).evaluate(with: email)
    }

    static func sanitizeString(_ input: String) -> String {
        let allowed = CharacterSet.alphanumerics.union(CharacterSet(charactersIn: " -_"))
        return input
            .components(separatedBy: allowed.inverted)
            .joined()
    }

    static func validateUrl(_ urlString: String) -> Bool {
        guard let url = URL(string: urlString) else { return false }
        return url.scheme == "https" && url.host != nil
    }
}
```

**Android Input Validation**:
```kotlin
class InputValidator {
    companion object {
        fun validateEmail(email: String): Boolean {
            val emailPattern = "^[A-Z0-9a-z._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}$"
            return email.matches(emailPattern.toRegex())
        }

        fun sanitizeString(input: String): String {
            return input.replace(Regex("[^a-zA-Z0-9\\s\\-_]"), "")
        }

        fun validateUrl(urlString: String): Boolean {
            return try {
                val url = URL(urlString)
                url.protocol == "https" && url.host != null
            } catch (e: Exception) {
                false
            }
        }
    }
}
```

### M5: Insecure Communication
**Vulnerability**: Unencrypted data in transit, weak TLS, or certificate validation bypass.

**iOS Network Security**:
```swift
import Foundation

class SecureNetworkManager {
    static let shared = SecureNetworkManager()

    func performSecureRequest(
        url: URL,
        completion: @escaping (Result<Data, Error>) -> Void
    ) {
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.timeoutInterval = 30

        // Enforce TLS 1.2+
        let config = URLSessionConfiguration.default
        config.tlsMinimumSupportedProtocolVersion = .TLSv12
        config.tlsMaximumSupportedProtocolVersion = .TLSv13

        let session = URLSession(
            configuration: config,
            delegate: CertificatePinningDelegate(),
            delegateQueue: nil
        )

        session.dataTask(with: request) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            guard let data = data else {
                completion(.failure(NetworkError.noData))
                return
            }
            completion(.success(data))
        }.resume()
    }
}

class CertificatePinningDelegate: NSObject, URLSessionDelegate {
    func urlSession(
        _ session: URLSession,
        didReceive challenge: URLAuthenticationChallenge,
        completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void
    ) {
        guard challenge.protectionSpace.authenticationMethod == NSURLAuthenticationMethodServerTrust,
              let trust = challenge.protectionSpace.serverTrust else {
            completionHandler(.cancelAuthenticationChallenge, nil)
            return
        }

        // Pin certificate public key
        let certificate = SecTrustGetCertificateAtIndex(trust, 0)
        let publicKey = SecCertificateCopyPublicKey(certificate!)
        let pinnedPublicKeyHash = publicKey.map { /* SHA-256 hash */ }

        completionHandler(.useCredential, URLCredential(trust: trust))
    }
}

enum NetworkError: Error {
    case noData
}
```

**Android Network Security**:
```kotlin
import okhttp3.OkHttpClient
import okhttp3.CertificatePinner
import java.util.concurrent.TimeUnit

class SecureNetworkManager {
    companion object {
        fun createSecureOkHttpClient(): OkHttpClient {
            val certificatePinner = CertificatePinner.Builder()
                .add("api.example.com", "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
                .build()

            return OkHttpClient.Builder()
                .certificatePinner(certificatePinner)
                .connectTimeout(30, TimeUnit.SECONDS)
                .readTimeout(30, TimeUnit.SECONDS)
                .writeTimeout(30, TimeUnit.SECONDS)
                .build()
        }
    }
}
```

### M6: Inadequate Privacy Controls
**Vulnerability**: Unnecessary data collection, lack of consent, or data leakage.

**iOS Privacy Implementation**:
```swift
import Foundation

class PrivacyManager {
    static let shared = PrivacyManager()

    // GDPR: Store consent status
    func requestUserConsent(for purpose: String) {
        UserDefaults.standard.setValue(
            true,
            forKey: "consent_\(purpose)"
        )
    }

    func hasConsent(for purpose: String) -> Bool {
        return UserDefaults.standard.bool(forKey: "consent_\(purpose)")
    }

    // CCPA: Right to deletion
    func deleteUserData() {
        UserDefaults.standard.removePersistentDomain(
            forName: Bundle.main.bundleIdentifier ?? ""
        )
    }

    // Privacy Manifest (iOS 17+)
    // Define in PrivacyInfo.xcprivacy
}
```

### M7: Code Obfuscation Issues
**Vulnerability**: Easily reversed bytecode or machine code enabling intellectual property theft.

**iOS Code Protection**:
```swift
// Swift compilation flags in Build Settings
// OTHER_SWIFT_FLAGS = -Osize -enforce-exclusivity=checked

// Obfuscate string literals
func obfuscatedString(_ encoded: String) -> String {
    // Use at runtime to prevent static string analysis
    return String(data: Data(base64Encoded: encoded) ?? Data(), encoding: .utf8) ?? ""
}

// Example: API_KEY = obfuscatedString("YWJjMTIz...")
```

**Android ProGuard Rules**:
```proguard
# proguard-rules.pro
-optimizationpasses 5
-verbose
-dontpreverify
-repackageclasses ''

# Keep API models but obfuscate implementation
-keep public class com.example.api.models.** { *; }
-keep,allowobfuscation class com.example.internal.** { *; }

# Remove logging
-assumenosideeffects class android.util.Log {
    public static *** d(...);
    public static *** v(...);
}

# Protect sensitive methods
-keepclassmembers class com.example.security.** {
    private <methods>;
}
```

### M8: Memory Safety Issues
**Vulnerability**: Buffer overflows, use-after-free, or memory leaks exposing sensitive data.

**iOS Memory Safety**:
```swift
// Swift is memory-safe by design, but avoid unsafe pointers
class SecureDataBuffer {
    private var data: [UInt8]

    init(size: Int) {
        data = [UInt8](repeating: 0, count: size)
    }

    // Clear sensitive data from memory
    func clear() {
        data.withUnsafeMutableBytes { buffer in
            memset(buffer.baseAddress, 0, buffer.count)
        }
    }

    deinit {
        clear()
    }
}
```

**Android Memory Safety**:
```kotlin
import java.security.SecureRandom

class SecureDataBuffer(size: Int) {
    private val buffer = ByteArray(size)

    fun clear() {
        SecureRandom().nextBytes(buffer)
        buffer.fill(0)
    }
}
```

### M9: Weak Reverse Engineering Protections
**Vulnerability**: Jailbreak/root detection bypass, easy symbolic execution, or insufficient anti-tampering.

**iOS Jailbreak Detection**:
```swift
class JailbreakDetection {
    static func isDeviceJailbroken() -> Bool {
        let jailbreakPaths = [
            "/Applications/Cydia.app",
            "/Library/MobileSubstrate/MobileSubstrate.dylib",
            "/bin/bash",
            "/usr/sbin/sshd"
        ]

        for path in jailbreakPaths {
            if FileManager.default.fileExists(atPath: path) {
                return true
            }
        }

        // Check for suspicious file permissions
        if canWriteToSystemDirectories() {
            return true
        }

        return false
    }

    private static func canWriteToSystemDirectories() -> Bool {
        let testFile = "/private/test_write_\(UUID().uuidString)"
        do {
            try "test".write(toFile: testFile, atomically: true, encoding: .utf8)
            try FileManager.default.removeItem(atPath: testFile)
            return true // Write succeeded - device is jailbroken
        } catch {
            return false
        }
    }
}
```

**Android Root Detection**:
```kotlin
import java.io.File

class RootDetection {
    companion object {
        fun isDeviceRooted(): Boolean {
            val paths = arrayOf(
                "/system/app/Superuser.apk",
                "/system/xbin/su",
                "/system/bin/su",
                "/data/local/xbin/su"
            )

            for (path in paths) {
                if (File(path).exists()) {
                    return true
                }
            }

            // Check for build properties
            val buildTags = android.os.Build.TAGS
            if (buildTags != null && buildTags.contains("test-keys")) {
                return true
            }

            return false
        }
    }
}
```

### M10: Extraneous Functionality
**Vulnerability**: Debug features, hidden backdoors, or unnecessary permissions enabled in production.

**iOS Cleanup**:
```swift
#if DEBUG
// Only enable debug features in debug builds
let debugMode = true
#else
let debugMode = false
#endif

class DebugManager {
    static func configureDebugFeatures() {
        #if DEBUG
        // Enable console logging only in debug
        enableDetailedLogging()
        #endif
    }
}
```

**Android Cleanup**:
```kotlin
object DebugConfig {
    val DEBUG_ENABLED = BuildConfig.DEBUG

    fun initializeApp() {
        if (!DEBUG_ENABLED) {
            // Disable debug features in release builds
            disableDebugBridge()
            removeSensitiveLogging()
        }
    }
}
```

---

## 2. Secure Data Storage

**iOS Keychain (Encrypted)**:
```swift
class KeychainStorage {
    static func store(_ data: String, key: String) throws {
        let dataToStore = data.data(using: .utf8)!
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecValueData as String: dataToStore,
            kSecAttrAccessible as String: kSecAttrAccessibleWhenUnlockedThisDeviceOnly,
            kSecAttrSynchronizable as String: false
        ]

        SecItemDelete(query as CFDictionary)
        let status = SecItemAdd(query as CFDictionary, nil)
        guard status == errSecSuccess else { throw StorageError.saveFailed }
    }
}
```

**Android EncryptedSharedPreferences**:
```kotlin
val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .build()

val prefs = EncryptedSharedPreferences.create(
    context,
    "secure_prefs",
    masterKey,
    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
)

prefs.edit().putString("key", "value").apply()
```

**Encrypted Database**:
```kotlin
// Android: Room with SQLCipher
val db = Room.databaseBuilder(
    context,
    AppDatabase::class.java,
    "encrypted.db"
)
    .openHelperFactory(SupportSQLiteOpenHelperFactory())
    .build()
```

---

## 3. Cryptography Implementation

**iOS AES-GCM Encryption**:
```swift
import CryptoKit

class CryptoManager {
    func encryptData(_ plaintext: String) throws -> (ciphertext: Data, nonce: Data) {
        let key = SymmetricKey(size: .bits256)
        let data = plaintext.data(using: .utf8)!
        let sealedBox = try AES.GCM.seal(data, using: key)
        return (sealedBox.ciphertext, sealedBox.nonce.withUnsafeBytes { Data($0) })
    }
}
```

**Android AES-GCM Encryption**:
```kotlin
import javax.crypto.Cipher
import javax.crypto.KeyGenerator

class CryptoManager {
    fun encryptData(plaintext: String): EncryptedData {
        val keyGen = KeyGenerator.getInstance("AES").apply {
            init(256)
        }
        val key = keyGen.generateKey()
        val cipher = Cipher.getInstance("AES/GCM/NoPadding").apply {
            init(Cipher.ENCRYPT_MODE, key)
        }
        val ciphertext = cipher.doFinal(plaintext.toByteArray())
        return EncryptedData(ciphertext, cipher.iv)
    }
}
```

**SHA-256 Hashing**:
```swift
import CryptoKit

let digest = SHA256.hash(data: "password".data(using: .utf8)!)
let hash = digest.map { String(format: "%02hhx", $0) }.joined()
```

---

## 4. Secure WebView Implementation

**iOS WKWebView Security**:
```swift
import WebKit

class SecureWebViewController: UIViewController, WKNavigationDelegate {
    let webView = WKWebView()

    override func viewDidLoad() {
        super.viewDidLoad()

        let prefs = WKWebpagePreferences()
        prefs.allowsContentJavaScript = true

        let config = WKWebViewConfiguration()
        config.defaultWebpagePreferences = prefs
        config.allowsInlineMediaPlayback = false
        config.mediaTypesRequiringUserActionForPlayback = .all

        webView.navigationDelegate = self
        webView.configuration.preferences.javaScriptEnabled = true

        loadSecurePage()
    }

    func loadSecurePage() {
        guard let url = URL(string: "https://example.com") else { return }
        let request = URLRequest(url: url)
        webView.load(request)
    }

    func webView(
        _ webView: WKWebView,
        decidePolicyFor navigationAction: WKNavigationAction,
        decisionHandler: @escaping (WKNavigationActionPolicy) -> Void
    ) {
        if let url = navigationAction.request.url,
           url.scheme == "https" {
            decisionHandler(.allow)
        } else {
            decisionHandler(.cancel)
        }
    }
}
```

**Android WebView Security**:
```kotlin
class SecureWebViewActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val webView = WebView(this)
        webView.settings.apply {
            javaScriptEnabled = false // Disable unless required
            domStorageEnabled = false
            databaseEnabled = false
            mixedContentMode = WebSettings.MIXED_CONTENT_NEVER_ALLOW
            allowFileAccess = false
            allowContentAccess = false
        }

        webView.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(
                view: WebView?,
                request: WebResourceRequest?
            ): Boolean {
                return request?.url?.scheme != "https"
            }
        }

        setContentView(webView)
    }
}
```

---

## 5. Secure Deep Link Validation

**iOS Deep Link Handler**:
```swift
class DeepLinkHandler {
    func handle(url: URL) -> Bool {
        guard let components = URLComponents(url: url, resolvingAgainstBaseURL: true) else {
            return false
        }

        guard url.scheme == "myapp" || url.scheme == "https" else {
            return false
        }

        guard let host = components.host, isValidHost(host) else {
            return false
        }

        route(to: components.path, with: components.queryItems ?? [])
        return true
    }

    private func isValidHost(_ host: String) -> Bool {
        let allowedHosts = ["example.com", "api.example.com"]
        return allowedHosts.contains(host)
    }
}
```

**Android Deep Link Validation**:
```kotlin
class DeepLinkHandler(private val context: Context) {
    fun handle(intent: Intent): Boolean {
        val uri = intent.data ?: return false

        // Validate scheme
        if (uri.scheme != "myapp" && uri.scheme != "https") {
            return false
        }

        // Validate host
        val validHosts = listOf("example.com", "api.example.com")
        if (!validHosts.contains(uri.host)) {
            return false
        }

        route(uri)
        return true
    }
}
```

---

## 6. RASP (Runtime Application Self-Protection)

**iOS RASP Implementation**:
```swift
class RASPMonitor {
    static func monitorSecurityThreats() {
        // Monitor debugger attachment
        if isDebuggerAttached() {
            handleSecurityThreat()
        }

        // Monitor code injection
        verifyCodeIntegrity()
    }

    private static func isDebuggerAttached() -> Bool {
        var info = kinfo_proc()
        var mib: [Int32] = [CTL_KERN, KERN_PROC, KERN_PROC_PID, getpid()]
        var size = MemoryLayout<kinfo_proc>.stride
        sysctl(&mib, 4, &info, &size, nil, 0)
        return (info.kp_proc.p_flag & P_TRACED) != 0
    }
}
```

**Android RASP Implementation**:
```kotlin
class RASPMonitor {
    companion object {
        fun monitorSecurityThreats(context: Context) {
            // Monitor debugger
            if (isDebuggerAttached()) {
                handleSecurityThreat()
            }

            // Monitor hooks
            verifyHooks()
        }

        private fun isDebuggerAttached(): Boolean {
            return Debug.isDebuggerConnected()
        }
    }
}
```

---

## 7. Binary Protections

**iOS Binary Hardening**:
```
Build Settings:
- Enable Bitcode
- Code Signing Identity
- Dead Code Stripping: Yes
- Strip Swift Symbols
- Deployment Target (minimum supported)
```

**Android Binary Hardening**:
```gradle
android {
    buildTypes {
        release {
            minifyEnabled true
            shrinkResources true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }

    packagingOptions {
        exclude 'META-INF/proguard/rules.pro'
    }
}
```

---

## 8. Privacy Compliance

**iOS Privacy Manifest**:
```xml
<!-- PrivacyInfo.xcprivacy -->
<key>NSPrivacyTracking</key>
<false/>
<key>NSPrivacyTrackingDomains</key>
<array/>
```

**GDPR/CCPA Compliance**:
```swift
class ComplianceManager {
    func requestGDPRConsent() {
        // Present consent screen
    }

    func deleteUserDataCCPA() {
        // Implement right to deletion
    }
}
```

---

## References
- OWASP Mobile Security Testing Guide (MSTG)
- Apple Security Engineering and Architecture (SEAR)
- Android Security Hardening
- NIST Mobile Security Guidelines
