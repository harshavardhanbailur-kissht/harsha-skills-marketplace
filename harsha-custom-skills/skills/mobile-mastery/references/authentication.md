# Mobile Authentication Reference Guide

Comprehensive guide to implementing secure authentication flows in mobile applications, covering iOS, Android, and cross-platform patterns.

## Table of Contents
1. [Auth Flows](#auth-flows)
2. [OAuth2/OIDC](#oauth2oidc)
3. [Biometric Authentication](#biometric-authentication)
4. [Session Management](#session-management)
5. [Multi-Factor Authentication](#multi-factor-authentication)
6. [Auth Providers](#auth-providers)
7. [Apple Sign In](#apple-sign-in)
8. [Google Sign In](#google-sign-in)
9. [Account Management](#account-management)
10. [Guest-to-Auth Migration](#guest-to-auth-migration)
11. [Security Best Practices](#security-best-practices)

---

## Auth Flows

### 1. Email/Password Authentication

**iOS Implementation (Swift)**
```swift
import Foundation

struct EmailPasswordAuth {
    let baseURL: URL
    let session: URLSession

    func signup(email: String, password: String) async throws -> AuthResponse {
        var request = URLRequest(url: baseURL.appendingPathComponent("/auth/signup"))
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let payload = SignupPayload(email: email, password: password)
        request.httpBody = try JSONEncoder().encode(payload)

        let (data, response) = try await session.data(for: request)
        guard (response as? HTTPURLResponse)?.statusCode == 201 else {
            throw AuthError.signupFailed
        }

        return try JSONDecoder().decode(AuthResponse.self, from: data)
    }

    func login(email: String, password: String) async throws -> AuthResponse {
        var request = URLRequest(url: baseURL.appendingPathComponent("/auth/login"))
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let payload = LoginPayload(email: email, password: password)
        request.httpBody = try JSONEncoder().encode(payload)

        let (data, response) = try await session.data(for: request)
        guard (response as? HTTPURLResponse)?.statusCode == 200 else {
            throw AuthError.loginFailed
        }

        return try JSONDecoder().decode(AuthResponse.self, from: data)
    }
}

struct SignupPayload: Codable {
    let email: String
    let password: String
}

struct LoginPayload: Codable {
    let email: String
    let password: String
}

struct AuthResponse: Codable {
    let accessToken: String
    let refreshToken: String
    let user: User
}
```

**Android Implementation (Kotlin)**
```kotlin
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import kotlinx.serialization.json.Json

class EmailPasswordAuth(private val baseURL: String) {
    private val client = OkHttpClient()
    private val json = Json { ignoreUnknownKeys = true }

    suspend fun signup(email: String, password: String): AuthResponse {
        val payload = SignupPayload(email, password)
        val requestBody = Json.encodeToString(payload)
            .toRequestBody("application/json".toMediaType())

        val request = Request.Builder()
            .url("$baseURL/auth/signup")
            .post(requestBody)
            .build()

        val response = client.newCall(request).execute()
        if (response.code != 201) throw AuthException.SignupFailed()

        return json.decodeFromString(response.body?.string() ?: "")
    }

    suspend fun login(email: String, password: String): AuthResponse {
        val payload = LoginPayload(email, password)
        val requestBody = Json.encodeToString(payload)
            .toRequestBody("application/json".toMediaType())

        val request = Request.Builder()
            .url("$baseURL/auth/login")
            .post(requestBody)
            .build()

        val response = client.newCall(request).execute()
        if (response.code != 200) throw AuthException.LoginFailed()

        return json.decodeFromString(response.body?.string() ?: "")
    }
}
```

### 2. Phone/OTP Authentication

**Swift Implementation**
```swift
struct PhoneOTPAuth {
    let baseURL: URL
    let session: URLSession

    func requestOTP(phoneNumber: String) async throws -> OTPResponse {
        var request = URLRequest(url: baseURL.appendingPathComponent("/auth/otp/request"))
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let payload = ["phoneNumber": phoneNumber]
        request.httpBody = try JSONSerialization.data(withJSONObject: payload)

        let (data, response) = try await session.data(for: request)
        guard (response as? HTTPURLResponse)?.statusCode == 200 else {
            throw AuthError.otpRequestFailed
        }

        return try JSONDecoder().decode(OTPResponse.self, from: data)
    }

    func verifyOTP(phoneNumber: String, code: String) async throws -> AuthResponse {
        var request = URLRequest(url: baseURL.appendingPathComponent("/auth/otp/verify"))
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let payload = ["phoneNumber": phoneNumber, "code": code]
        request.httpBody = try JSONSerialization.data(withJSONObject: payload)

        let (data, response) = try await session.data(for: request)
        guard (response as? HTTPURLResponse)?.statusCode == 200 else {
            throw AuthError.otpVerificationFailed
        }

        return try JSONDecoder().decode(AuthResponse.self, from: data)
    }
}

struct OTPResponse: Codable {
    let expiresIn: Int
    let sessionId: String
}
```

### 3. Magic Link Authentication

**Swift Implementation**
```swift
struct MagicLinkAuth {
    let baseURL: URL
    let session: URLSession

    func sendMagicLink(email: String) async throws -> MagicLinkResponse {
        var request = URLRequest(url: baseURL.appendingPathComponent("/auth/magic-link/send"))
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let payload = ["email": email]
        request.httpBody = try JSONSerialization.data(withJSONObject: payload)

        let (data, response) = try await session.data(for: request)
        guard (response as? HTTPURLResponse)?.statusCode == 200 else {
            throw AuthError.magicLinkFailed
        }

        return try JSONDecoder().decode(MagicLinkResponse.self, from: data)
    }

    func handleMagicLink(token: String) async throws -> AuthResponse {
        var request = URLRequest(url: baseURL.appendingPathComponent("/auth/magic-link/verify"))
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let payload = ["token": token]
        request.httpBody = try JSONSerialization.data(withJSONObject: payload)

        let (data, response) = try await session.data(for: request)
        guard (response as? HTTPURLResponse)?.statusCode == 200 else {
            throw AuthError.invalidMagicLink
        }

        return try JSONDecoder().decode(AuthResponse.self, from: data)
    }
}
```

### 4. Passkeys/WebAuthn

**Swift Implementation**
```swift
import AuthenticationServices

@available(iOS 16.0, *)
struct PasskeyAuth: NSObject, ASAuthorizationControllerPresentationContextProviding {
    let baseURL: URL
    let session: URLSession
    var window: UIWindow?

    func createPasskey(email: String, challenge: String) async throws -> PasskeyResponse {
        let request = ASAuthorizationPlatformPublicKeyCredentialProvider(relyingPartyIdentifier: "app.example.com")
            .createCredentialRegistrationRequest(challenge: challenge.data(using: .utf8)!)

        request.userID = email.data(using: .utf8)!
        request.userName = email
        request.userDisplayName = email

        let controller = ASAuthorizationController(authorizationRequests: [request])
        controller.presentationContextProvider = self

        // Handle response in delegate methods
        return try await withCheckedThrowingContinuation { continuation in
            // Store continuation for delegate callback
        }
    }

    func authorizationController(controller: ASAuthorizationController, didCompleteWithAuthorization authorization: ASAuthorization) {
        if let credential = authorization.credential as? ASAuthorizationPlatformPublicKeyCredentialRegistration {
            let attestationObject = credential.rawAttestationObject
            let clientDataJSON = credential.rawClientDataJSON
            // Send to server for verification
        }
    }

    func presentationAnchor(for controller: ASAuthorizationController) -> ASPresentationAnchor {
        return window ?? ASPresentationAnchor()
    }
}
```

---

## OAuth2/OIDC

### Authorization Code Flow with PKCE (Mandatory)

**Swift Implementation**
```swift
import Foundation
import CryptoKit

struct OAuth2Manager {
    let clientID: String
    let clientSecret: String
    let redirectURL: URL
    let authorizationEndpoint: URL
    let tokenEndpoint: URL
    let baseURL: URL

    // PKCE: Generate challenge and verifier
    func generatePKCE() -> (challenge: String, verifier: String) {
        let verifier = Data((0..<32).map { _ in UInt8.random(in: 0...255) })
            .base64EncodedString()
            .replacingOccurrences(of: "+", with: "-")
            .replacingOccurrences(of: "/", with: "_")
            .trimmingCharacters(in: CharacterSet(charactersIn: "="))

        let challenge = Data(SHA256.hash(data: verifier.data(using: .utf8)!))
            .base64EncodedString()
            .replacingOccurrences(of: "+", with: "-")
            .replacingOccurrences(of: "/", with: "_")
            .trimmingCharacters(in: CharacterSet(charactersIn: "="))

        return (challenge, verifier)
    }

    // Generate authorization URL
    func getAuthorizationURL(codeChallenge: String) -> URL {
        var components = URLComponents(url: authorizationEndpoint, resolvingAgainstBaseURL: true)!
        components.queryItems = [
            URLQueryItem(name: "client_id", value: clientID),
            URLQueryItem(name: "redirect_uri", value: redirectURL.absoluteString),
            URLQueryItem(name: "response_type", value: "code"),
            URLQueryItem(name: "scope", value: "openid profile email"),
            URLQueryItem(name: "code_challenge", value: codeChallenge),
            URLQueryItem(name: "code_challenge_method", value: "S256"),
            URLQueryItem(name: "state", value: UUID().uuidString)
        ]
        return components.url!
    }

    // Exchange authorization code for tokens
    func exchangeCodeForToken(code: String, codeVerifier: String) async throws -> TokenResponse {
        var request = URLRequest(url: tokenEndpoint)
        request.httpMethod = "POST"
        request.setValue("application/x-www-form-urlencoded", forHTTPHeaderField: "Content-Type")

        let body = [
            "grant_type": "authorization_code",
            "code": code,
            "client_id": clientID,
            "client_secret": clientSecret,
            "redirect_uri": redirectURL.absoluteString,
            "code_verifier": codeVerifier
        ]

        let bodyString = body.map { "\($0.key)=\($0.value)" }.joined(separator: "&")
        request.httpBody = bodyString.data(using: .utf8)

        let (data, response) = try await URLSession.shared.data(for: request)
        guard (response as? HTTPURLResponse)?.statusCode == 200 else {
            throw OAuthError.tokenExchangeFailed
        }

        return try JSONDecoder().decode(TokenResponse.self, from: data)
    }
}

struct TokenResponse: Codable {
    let accessToken: String
    let refreshToken: String?
    let idToken: String?
    let expiresIn: Int
    let tokenType: String

    enum CodingKeys: String, CodingKey {
        case accessToken = "access_token"
        case refreshToken = "refresh_token"
        case idToken = "id_token"
        case expiresIn = "expires_in"
        case tokenType = "token_type"
    }
}
```

### Token Management

**Swift Implementation**
```swift
import Foundation

class TokenManager {
    private let tokenKey = "oauth_tokens"
    private let keychainService = "com.app.oauth"

    func saveTokens(_ tokens: TokenResponse) throws {
        let data = try JSONEncoder().encode(tokens)
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: keychainService,
            kSecValueData as String: data
        ]

        SecItemDelete(query as CFDictionary)
        let status = SecItemAdd(query as CFDictionary, nil)
        guard status == errSecSuccess else { throw TokenError.saveFailed }
    }

    func getTokens() throws -> TokenResponse? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: keychainService,
            kSecReturnData as String: true
        ]

        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)

        guard status == errSecSuccess, let data = result as? Data else {
            return nil
        }

        return try JSONDecoder().decode(TokenResponse.self, from: data)
    }

    func refreshAccessToken(using refreshToken: String, with manager: OAuth2Manager) async throws -> TokenResponse {
        var request = URLRequest(url: manager.tokenEndpoint)
        request.httpMethod = "POST"
        request.setValue("application/x-www-form-urlencoded", forHTTPHeaderField: "Content-Type")

        let body = [
            "grant_type": "refresh_token",
            "refresh_token": refreshToken,
            "client_id": manager.clientID,
            "client_secret": manager.clientSecret
        ]

        let bodyString = body.map { "\($0.key)=\($0.value)" }.joined(separator: "&")
        request.httpBody = bodyString.data(using: .utf8)

        let (data, response) = try await URLSession.shared.data(for: request)
        guard (response as? HTTPURLResponse)?.statusCode == 200 else {
            throw TokenError.refreshFailed
        }

        let newTokens = try JSONDecoder().decode(TokenResponse.self, from: data)
        try saveTokens(newTokens)
        return newTokens
    }

    func isTokenExpired(_ token: TokenResponse) -> Bool {
        let expiryDate = Date(timeIntervalSinceNow: TimeInterval(token.expiresIn))
        return Date() >= expiryDate.addingTimeInterval(-300) // 5-minute buffer
    }
}
```

---

## Biometric Authentication

### iOS: Face ID / Touch ID

**Swift Implementation**
```swift
import LocalAuthentication

class BiometricAuth {
    let context = LAContext()

    func canUseBiometrics() -> Bool {
        var error: NSError?
        return context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error)
    }

    func biometricType() -> LABiometryType {
        context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: nil)
        return context.biometryType
    }

    func authenticate() async throws -> Bool {
        let reason = "Authenticate to access your account"

        do {
            return try await context.evaluatePolicy(
                .deviceOwnerAuthenticationWithBiometrics,
                localizedReason: reason
            )
        } catch let error as NSError {
            switch error.code {
            case LAError.authenticationFailed.rawValue:
                throw BiometricError.authenticationFailed
            case LAError.userCancel.rawValue:
                throw BiometricError.userCancelled
            case LAError.userFallback.rawValue:
                throw BiometricError.userFallback
            case LAError.biometryNotAvailable.rawValue:
                throw BiometricError.notAvailable
            default:
                throw BiometricError.unknown
            }
        }
    }

    func saveBiometricCredentials(username: String, password: String) throws {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: username,
            kSecValueData as String: password.data(using: .utf8)!,
            kSecUseDataProtection as String: kSecAttrAccessibleWhenPasscodeSetThisDeviceOnly
        ]

        SecItemDelete(query as CFDictionary)
        let status = SecItemAdd(query as CFDictionary, nil)
        guard status == errSecSuccess else { throw BiometricError.saveFailed }
    }

    func retrieveBiometricCredentials(username: String) throws -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: username,
            kSecReturnData as String: true
        ]

        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)

        guard status == errSecSuccess, let data = result as? Data else {
            return nil
        }

        return String(data: data, encoding: .utf8)
    }
}

enum BiometricError: Error {
    case authenticationFailed
    case userCancelled
    case userFallback
    case notAvailable
    case saveFailed
    case unknown
}
```

### Android: BiometricPrompt

**Kotlin Implementation**
```kotlin
import androidx.biometric.BiometricPrompt
import androidx.fragment.app.Fragment
import androidx.fragment.app.FragmentActivity
import java.util.concurrent.Executor
import android.os.CancellationSignal

class BiometricAuth(private val activity: FragmentActivity) {
    private val executor: Executor = ContextCompat.getMainExecutor(activity)

    fun canUseBiometrics(): Boolean {
        val biometricManager = BiometricManager.from(activity)
        return biometricManager.canAuthenticate(
            BiometricManager.Authenticators.BIOMETRIC_STRONG
        ) == BiometricManager.BIOMETRIC_SUCCESS
    }

    fun authenticate(
        onSuccess: (BiometricPrompt.AuthenticationResult) -> Unit,
        onError: (Int, CharSequence) -> Unit
    ) {
        val biometricPrompt = BiometricPrompt(
            activity,
            executor,
            object : BiometricPrompt.AuthenticationCallback() {
                override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
                    super.onAuthenticationSucceeded(result)
                    onSuccess(result)
                }

                override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                    super.onAuthenticationError(errorCode, errString)
                    onError(errorCode, errString)
                }

                override fun onAuthenticationFailed() {
                    super.onAuthenticationFailed()
                    // Handle failed authentication
                }
            }
        )

        val promptInfo = BiometricPrompt.PromptInfo.Builder()
            .setTitle("Biometric Login")
            .setSubtitle("Use your fingerprint or face to login")
            .setNegativeButtonText("Cancel")
            .build()

        biometricPrompt.authenticate(promptInfo)
    }

    fun saveBiometricCredentials(username: String, password: String) {
        val encryptedSharedPreferences = EncryptedSharedPreferences.create(
            activity,
            "bio_prefs",
            MasterKey.Builder(activity).setKeyScheme(MasterKey.KeyScheme.AES256_GCM).build(),
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        )

        encryptedSharedPreferences.edit().apply {
            putString("username_$username", password)
            apply()
        }
    }

    fun retrieveBiometricCredentials(username: String): String? {
        val encryptedSharedPreferences = EncryptedSharedPreferences.create(
            activity,
            "bio_prefs",
            MasterKey.Builder(activity).setKeyScheme(MasterKey.KeyScheme.AES256_GCM).build(),
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        )

        return encryptedSharedPreferences.getString("username_$username", null)
    }
}
```

---

## Session Management

### JWT Storage and Refresh

**Swift Implementation**
```swift
import Foundation

class SessionManager {
    static let shared = SessionManager()
    private let keychainService = "com.app.session"
    private let userDefaults = UserDefaults.standard

    // Store JWT in Keychain (secure)
    func saveJWT(_ token: String) throws {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: keychainService,
            kSecAttrAccount as String: "jwt_token",
            kSecValueData as String: token.data(using: .utf8)!,
            kSecUseDataProtection as String: kSecAttrAccessibleWhenPasscodeSetThisDeviceOnly
        ]

        SecItemDelete(query as CFDictionary)
        let status = SecItemAdd(query as CFDictionary, nil)
        guard status == errSecSuccess else { throw SessionError.saveJWTFailed }
    }

    func getJWT() -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: keychainService,
            kSecAttrAccount as String: "jwt_token",
            kSecReturnData as String: true
        ]

        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)

        guard status == errSecSuccess, let data = result as? Data else {
            return nil
        }

        return String(data: data, encoding: .utf8)
    }

    // Decode JWT payload (without verification - for local use only)
    func decodeJWT(_ token: String) -> JWTPayload? {
        let parts = token.split(separator: ".")
        guard parts.count == 3 else { return nil }

        var base64 = String(parts[1])
        base64 += String(repeating: "=", count: (4 - base64.count % 4) % 4)

        guard let data = Data(base64Encoded: base64),
              let json = try? JSONDecoder().decode(JWTPayload.self, from: data) else {
            return nil
        }

        return json
    }

    // Check if JWT is expired
    func isJWTExpired(_ token: String) -> Bool {
        guard let payload = decodeJWT(token) else { return true }
        let expiryDate = Date(timeIntervalSince1970: TimeInterval(payload.exp))
        return Date() >= expiryDate.addingTimeInterval(-300) // 5-minute buffer
    }

    func logout() throws {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: keychainService
        ]

        let status = SecItemDelete(query as CFDictionary)
        guard status == errSecSuccess else { throw SessionError.logoutFailed }
    }
}

struct JWTPayload: Codable {
    let sub: String
    let email: String
    let iat: Int
    let exp: Int
}

enum SessionError: Error {
    case saveJWTFailed
    case logoutFailed
}
```

### Token Refresh Strategy

**Swift Implementation**
```swift
class AuthInterceptor: URLSessionDelegate {
    let tokenManager: TokenManager
    let oauth2Manager: OAuth2Manager

    func refreshTokenIfNeeded() async throws -> String {
        guard let tokens = try tokenManager.getTokens() else {
            throw AuthError.noTokensAvailable
        }

        if tokenManager.isTokenExpired(tokens) {
            guard let refreshToken = tokens.refreshToken else {
                throw AuthError.cannotRefreshToken
            }

            let newTokens = try await tokenManager.refreshAccessToken(
                using: refreshToken,
                with: oauth2Manager
            )

            return newTokens.accessToken
        }

        return tokens.accessToken
    }

    // For URLSession configuration
    func addAuthorizationHeader(to request: inout URLRequest) async throws {
        let token = try await refreshTokenIfNeeded()
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
    }
}
```

---

## Multi-Factor Authentication

### TOTP (Time-based One-Time Password)

**Swift Implementation**
```swift
import Foundation
import CryptoKit

struct TOTPAuth {
    let secret: String
    let issuer: String = "MyApp"

    func generateTOTP() -> String {
        let interval = Int(Date().timeIntervalSince1970) / 30
        let data = withUnsafeBytes(of: interval.bigEndian) { Data($0) }

        guard let secretData = Data(base64Encoded: secret) else { return "" }

        let signature = HMAC<SHA1>.authenticationCode(for: data, using: SymmetricKey(data: secretData))
        let bytes = Array(signature)
        let offset = Int(bytes[bytes.count - 1]) & 0xf
        let truncated = UInt32(bytes[offset] & 0x7f) << 24 |
                       UInt32(bytes[offset + 1]) << 16 |
                       UInt32(bytes[offset + 2]) << 8 |
                       UInt32(bytes[offset + 3])

        let otp = (truncated % 1_000_000)
        return String(format: "%06d", otp)
    }

    func verifyTOTP(_ code: String) -> Bool {
        let generatedCode = generateTOTP()
        return generatedCode == code
    }

    // Generate QR code URL for authenticator apps
    func getOTPAuthURL(email: String) -> URL {
        let label = "\(issuer):\(email)"
        let urlString = "otpauth://totp/\(label)?secret=\(secret)&issuer=\(issuer)"
        return URL(string: urlString.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed)!)!
    }
}
```

### SMS MFA

**Swift Implementation**
```swift
struct SMSMFAAuth {
    let baseURL: URL
    let session: URLSession

    func requestSMSCode(phoneNumber: String) async throws -> SMSResponse {
        var request = URLRequest(url: baseURL.appendingPathComponent("/mfa/sms/request"))
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let payload = ["phoneNumber": phoneNumber]
        request.httpBody = try JSONSerialization.data(withJSONObject: payload)

        let (data, response) = try await session.data(for: request)
        guard (response as? HTTPURLResponse)?.statusCode == 200 else {
            throw MFAError.smsRequestFailed
        }

        return try JSONDecoder().decode(SMSResponse.self, from: data)
    }

    func verifySMSCode(sessionId: String, code: String) async throws -> Bool {
        var request = URLRequest(url: baseURL.appendingPathComponent("/mfa/sms/verify"))
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let payload = ["sessionId": sessionId, "code": code]
        request.httpBody = try JSONSerialization.data(withJSONObject: payload)

        let (data, response) = try await session.data(for: request)
        guard (response as? HTTPURLResponse)?.statusCode == 200 else {
            throw MFAError.verificationFailed
        }

        let result = try JSONDecoder().decode(VerificationResult.self, from: data)
        return result.verified
    }
}

struct SMSResponse: Codable {
    let sessionId: String
    let expiresIn: Int
}

struct VerificationResult: Codable {
    let verified: Bool
}

enum MFAError: Error {
    case smsRequestFailed
    case verificationFailed
}
```

### Push-based Verification

**Swift Implementation**
```swift
import UserNotifications

struct PushMFAAuth {
    let baseURL: URL
    let session: URLSession

    func requestPushApproval(userId: String) async throws -> PushResponse {
        var request = URLRequest(url: baseURL.appendingPathComponent("/mfa/push/request"))
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let payload = ["userId": userId]
        request.httpBody = try JSONSerialization.data(withJSONObject: payload)

        let (data, response) = try await session.data(for: request)
        guard (response as? HTTPURLResponse)?.statusCode == 200 else {
            throw MFAError.pushRequestFailed
        }

        return try JSONDecoder().decode(PushResponse.self, from: data)
    }

    func handlePushApproval(requestId: String, approved: Bool) async throws {
        var request = URLRequest(url: baseURL.appendingPathComponent("/mfa/push/respond"))
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let payload = ["requestId": requestId, "approved": approved]
        request.httpBody = try JSONSerialization.data(withJSONObject: payload)

        let (_, response) = try await session.data(for: request)
        guard (response as? HTTPURLResponse)?.statusCode == 200 else {
            throw MFAError.pushResponseFailed
        }
    }
}

struct PushResponse: Codable {
    let requestId: String
    let expiresIn: Int
}
```

---

## Auth Providers

### Firebase Authentication

**Swift Setup**
```swift
import FirebaseAuth

class FirebaseAuthManager {
    static let shared = FirebaseAuthManager()
    private var authStateHandle: AuthStateDidChangeListenerHandle?

    func signupWithEmail(email: String, password: String) async throws -> User {
        let result = try await Auth.auth().createUser(withEmail: email, password: password)
        return result.user
    }

    func loginWithEmail(email: String, password: String) async throws -> User {
        let result = try await Auth.auth().signIn(withEmail: email, password: password)
        return result.user
    }

    func sendPasswordReset(email: String) async throws {
        try await Auth.auth().sendPasswordReset(withEmail: email)
    }

    func listenToAuthState(completion: @escaping (User?) -> Void) {
        authStateHandle = Auth.auth().addStateDidChangeListener { _, user in
            completion(user)
        }
    }

    func removeAuthStateListener() {
        if let handle = authStateHandle {
            Auth.auth().removeStateDidChangeListener(handle)
        }
    }

    func logout() throws {
        try Auth.auth().signOut()
    }

    func getIDToken() async throws -> String {
        guard let user = Auth.auth().currentUser else { throw AuthError.notAuthenticated }
        return try await user.getIDToken()
    }
}
```

**Kotlin Setup**
```kotlin
import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.auth.ktx.auth
import com.google.firebase.ktx.Firebase

class FirebaseAuthManager {
    private val auth = Firebase.auth

    suspend fun signupWithEmail(email: String, password: String): AuthResult {
        return try {
            val result = auth.createUserWithEmailAndPassword(email, password).await()
            AuthResult.Success(result.user)
        } catch (e: Exception) {
            AuthResult.Error(e.message ?: "Signup failed")
        }
    }

    suspend fun loginWithEmail(email: String, password: String): AuthResult {
        return try {
            val result = auth.signInWithEmailAndPassword(email, password).await()
            AuthResult.Success(result.user)
        } catch (e: Exception) {
            AuthResult.Error(e.message ?: "Login failed")
        }
    }

    fun logout() {
        auth.signOut()
    }

    fun getCurrentUser() = auth.currentUser
}
```

### Supabase Auth

**Swift Setup**
```swift
import Supabase

class SupabaseAuthManager {
    let client = SupabaseClient(supabaseURL: URL(string: "https://your-project.supabase.co")!, supabaseKey: "your-anon-key")

    func signupWithEmail(email: String, password: String) async throws -> User {
        let response = try await client.auth.signUp(email: email, password: password)
        return response.user
    }

    func loginWithEmail(email: String, password: String) async throws -> Session {
        return try await client.auth.signIn(email: email, password: password)
    }

    func logout() async throws {
        try await client.auth.signOut()
    }

    func refreshSession() async throws -> Session {
        return try await client.auth.refreshSession()
    }
}
```

### Auth0

**Swift Setup**
```swift
import Auth0

class Auth0Manager {
    let webAuth = Auth0.webAuth()

    func login(completion: @escaping (Auth0Error?) -> Void) {
        webAuth
            .scope("openid profile email")
            .audience("your-api-identifier")
            .start { result in
                switch result {
                case .success(let credentials):
                    self.saveCredentials(credentials)
                    completion(nil)
                case .failure(let error):
                    completion(error)
                }
            }
    }

    func getAccessToken() -> String? {
        guard let credentials = CredentialsManager(authentication: Auth0.authentication()).credentials() else {
            return nil
        }
        return credentials.accessToken
    }

    func logout() throws {
        try CredentialsManager(authentication: Auth0.authentication()).clear()
    }
}
```

### AWS Cognito

**Swift Setup**
```swift
import AWSCognitoIdentityProvider

class CognitoAuthManager {
    let userPool: AWSCognitoIdentityUserPool

    init(poolId: String, clientId: String, region: AWSRegionType) {
        let config = AWSServiceConfiguration(region: region, credentialsProvider: nil)
        AWSServiceManager.default().defaultServiceConfiguration = config

        self.userPool = AWSCognitoIdentityUserPool(forKey: "userPool")
    }

    func signup(email: String, password: String, attributes: [String: String]) async throws {
        let signupRequest = userPool.signUp(email, password: password, userAttributes: attributes)

        return try await withCheckedThrowingContinuation { continuation in
            signupRequest.continueWith { task in
                if let error = task.error {
                    continuation.resume(throwing: error)
                } else {
                    continuation.resume()
                }
                return nil
            }
        }
    }

    func confirmSignup(username: String, confirmationCode: String) async throws {
        let user = userPool.getUser(username)

        return try await withCheckedThrowingContinuation { continuation in
            user.confirmSignUp(confirmationCode).continueWith { task in
                if let error = task.error {
                    continuation.resume(throwing: error)
                } else {
                    continuation.resume()
                }
                return nil
            }
        }
    }
}
```

---

## Apple Sign In

**Swift Implementation**
```swift
import AuthenticationServices

class AppleSignInManager: NSObject, ASAuthorizationControllerDelegate, ASAuthorizationControllerPresentationContextProviding {
    var window: UIWindow?
    var completionHandler: ((Result<ASAuthorizationAppleIDCredential, Error>) -> Void)?

    func initiateAppleSignIn() {
        let appleIDProvider = ASAuthorizationAppleIDProvider()
        let request = appleIDProvider.createRequest()
        request.requestedScopes = [.fullName, .email]

        let authorizationController = ASAuthorizationController(authorizationRequests: [request])
        authorizationController.delegate = self
        authorizationController.presentationContextProvider = self
        authorizationController.performRequests()
    }

    // MARK: - ASAuthorizationControllerDelegate

    func authorizationController(
        controller: ASAuthorizationController,
        didCompleteWithAuthorization authorization: ASAuthorization
    ) {
        if let appleIDCredential = authorization.credential as? ASAuthorizationAppleIDCredential {
            let userIdentifier = appleIDCredential.user
            let firstName = appleIDCredential.fullName?.givenName ?? ""
            let email = appleIDCredential.email ?? ""
            let identityToken = appleIDCredential.identityToken
            let authorizationCode = appleIDCredential.authorizationCode

            // Send to backend for verification
            self.sendAppleIDCredentialToBackend(
                identifier: userIdentifier,
                firstName: firstName,
                email: email,
                identityToken: identityToken,
                authorizationCode: authorizationCode
            )

            completionHandler?(.success(appleIDCredential))
        }
    }

    func authorizationController(controller: ASAuthorizationController, didCompleteWithError error: Error) {
        completionHandler?(.failure(error))
    }

    // MARK: - ASAuthorizationControllerPresentationContextProviding

    func presentationAnchor(for controller: ASAuthorizationController) -> ASPresentationAnchor {
        return window ?? ASPresentationAnchor()
    }

    // MARK: - Backend Communication

    private func sendAppleIDCredentialToBackend(
        identifier: String,
        firstName: String,
        email: String,
        identityToken: Data?,
        authorizationCode: Data?
    ) {
        var request = URLRequest(url: URL(string: "https://api.example.com/auth/apple")!)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let payload: [String: Any] = [
            "identifier": identifier,
            "firstName": firstName,
            "email": email,
            "identityToken": identityToken?.base64EncodedString() ?? "",
            "authorizationCode": authorizationCode?.base64EncodedString() ?? ""
        ]

        request.httpBody = try? JSONSerialization.data(withJSONObject: payload)

        URLSession.shared.dataTask(with: request) { data, response, error in
            // Handle response
        }.resume()
    }
}
```

---

## Google Sign In

### iOS Implementation

**Swift Setup**
```swift
import GoogleSignIn

class GoogleSignInManager {
    static let shared = GoogleSignInManager()

    func signIn(presenting viewController: UIViewController) async throws -> GIDGoogleUser? {
        do {
            let result = try await GIDSignIn.sharedInstance.signIn(
                withPresenting: viewController
            )

            let user = result.user
            let email = user.profile?.email ?? ""
            let displayName = user.profile?.name ?? ""
            let idToken = user.idToken?.tokenString ?? ""

            return user
        } catch {
            throw GoogleSignInError.signInFailed(error)
        }
    }

    func signOut() {
        GIDSignIn.sharedInstance.signOut()
    }

    func restorePreviousSignIn() async -> GIDGoogleUser? {
        do {
            return try await GIDSignIn.sharedInstance.restorePreviousSignIn()
        } catch {
            return nil
        }
    }
}

enum GoogleSignInError: Error {
    case signInFailed(Error)
    case noUser
}
```

### Android Implementation

**Kotlin Setup**
```kotlin
import com.google.android.gms.auth.api.signin.GoogleSignIn
import com.google.android.gms.auth.api.signin.GoogleSignInClient
import com.google.android.gms.auth.api.signin.GoogleSignInOptions
import android.app.Activity
import androidx.activity.result.contract.ActivityResultContracts

class GoogleSignInManager(private val activity: Activity) {
    private lateinit var googleSignInClient: GoogleSignInClient

    fun initialize(clientId: String) {
        val gso = GoogleSignInOptions.Builder(GoogleSignInOptions.DEFAULT_SIGN_IN)
            .requestIdToken(clientId)
            .requestEmail()
            .build()

        googleSignInClient = GoogleSignIn.getClient(activity, gso)
    }

    fun signIn(onSuccess: (GoogleSignInAccount?) -> Unit, onFailure: (Exception) -> Unit) {
        val signInIntent = googleSignInClient.signInIntent
        activity.startActivityForResult(signInIntent, RC_SIGN_IN)
    }

    fun signOut() {
        googleSignInClient.signOut()
    }

    fun handleSignInResult(data: Intent?) {
        try {
            val task = GoogleSignIn.getSignedInAccountFromIntent(data)
            val account = task.result
            // Send account info to backend
        } catch (e: ApiException) {
            // Handle error
        }
    }

    companion object {
        const val RC_SIGN_IN = 9001
    }
}
```

---

## Account Management

### Account Linking

**Swift Implementation**
```swift
struct AccountLinkingManager {
    let baseURL: URL
    let session: URLSession

    func linkProvider(
        userId: String,
        provider: String,
        accessToken: String,
        idToken: String? = nil
    ) async throws -> LinkingResult {
        var request = URLRequest(url: baseURL.appendingPathComponent("/account/link"))
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("Bearer \(try SessionManager.shared.getJWT() ?? "")", forHTTPHeaderField: "Authorization")

        let payload: [String: String?] = [
            "userId": userId,
            "provider": provider,
            "accessToken": accessToken,
            "idToken": idToken
        ]

        request.httpBody = try JSONSerialization.data(withJSONObject: payload)

        let (data, response) = try await session.data(for: request)
        guard (response as? HTTPURLResponse)?.statusCode == 200 else {
            throw AccountError.linkingFailed
        }

        return try JSONDecoder().decode(LinkingResult.self, from: data)
    }

    func unlinkProvider(userId: String, provider: String) async throws {
        var request = URLRequest(url: baseURL.appendingPathComponent("/account/unlink"))
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("Bearer \(try SessionManager.shared.getJWT() ?? "")", forHTTPHeaderField: "Authorization")

        let payload = ["userId": userId, "provider": provider]
        request.httpBody = try JSONSerialization.data(withJSONObject: payload)

        let (_, response) = try await session.data(for: request)
        guard (response as? HTTPURLResponse)?.statusCode == 200 else {
            throw AccountError.unlinkingFailed
        }
    }
}

struct LinkingResult: Codable {
    let success: Bool
    let providers: [String]
}

enum AccountError: Error {
    case linkingFailed
    case unlinkingFailed
}
```

### Password Reset

**Swift Implementation**
```swift
struct PasswordResetManager {
    let baseURL: URL
    let session: URLSession

    func requestPasswordReset(email: String) async throws {
        var request = URLRequest(url: baseURL.appendingPathComponent("/account/password-reset/request"))
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let payload = ["email": email]
        request.httpBody = try JSONSerialization.data(withJSONObject: payload)

        let (_, response) = try await session.data(for: request)
        guard (response as? HTTPURLResponse)?.statusCode == 200 else {
            throw ResetError.requestFailed
        }
    }

    func resetPassword(token: String, newPassword: String) async throws {
        var request = URLRequest(url: baseURL.appendingPathComponent("/account/password-reset/confirm"))
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let payload = ["token": token, "newPassword": newPassword]
        request.httpBody = try JSONSerialization.data(withJSONObject: payload)

        let (_, response) = try await session.data(for: request)
        guard (response as? HTTPURLResponse)?.statusCode == 200 else {
            throw ResetError.resetFailed
        }
    }
}

enum ResetError: Error {
    case requestFailed
    case resetFailed
}
```

### Email Verification

**Swift Implementation**
```swift
struct EmailVerificationManager {
    let baseURL: URL
    let session: URLSession

    func sendVerificationEmail(userId: String) async throws {
        var request = URLRequest(url: baseURL.appendingPathComponent("/account/email-verification/send"))
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("Bearer \(try SessionManager.shared.getJWT() ?? "")", forHTTPHeaderField: "Authorization")

        let payload = ["userId": userId]
        request.httpBody = try JSONSerialization.data(withJSONObject: payload)

        let (_, response) = try await session.data(for: request)
        guard (response as? HTTPURLResponse)?.statusCode == 200 else {
            throw VerificationError.sendFailed
        }
    }

    func verifyEmail(token: String) async throws -> Bool {
        var request = URLRequest(url: baseURL.appendingPathComponent("/account/email-verification/confirm"))
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let payload = ["token": token]
        request.httpBody = try JSONSerialization.data(withJSONObject: payload)

        let (data, response) = try await session.data(for: request)
        guard (response as? HTTPURLResponse)?.statusCode == 200 else {
            throw VerificationError.verificationFailed
        }

        let result = try JSONDecoder().decode(VerificationConfirmResult.self, from: data)
        return result.verified
    }
}

struct VerificationConfirmResult: Codable {
    let verified: Bool
}

enum VerificationError: Error {
    case sendFailed
    case verificationFailed
}
```

---

## Guest-to-Auth Migration

**Swift Implementation**
```swift
class GuestAuthMigrationManager {
    let baseURL: URL
    let session: URLSession

    // Create guest session (anonymous)
    func createGuestSession() async throws -> GuestSessionResponse {
        var request = URLRequest(url: baseURL.appendingPathComponent("/auth/guest"))
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let (data, response) = try await session.data(for: request)
        guard (response as? HTTPURLResponse)?.statusCode == 201 else {
            throw GuestError.sessionCreationFailed
        }

        let guestSession = try JSONDecoder().decode(GuestSessionResponse.self, from: data)
        try SessionManager.shared.saveGuestToken(guestSession.accessToken)
        return guestSession
    }

    // Migrate guest data to authenticated user
    func migrateGuestToAuth(
        guestToken: String,
        email: String,
        password: String
    ) async throws -> AuthResponse {
        var request = URLRequest(url: baseURL.appendingPathComponent("/auth/migrate"))
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("Bearer \(guestToken)", forHTTPHeaderField: "Authorization")

        let payload = ["email": email, "password": password]
        request.httpBody = try JSONSerialization.data(withJSONObject: payload)

        let (data, response) = try await session.data(for: request)
        guard (response as? HTTPURLResponse)?.statusCode == 200 else {
            throw GuestError.migrationFailed
        }

        let authResponse = try JSONDecoder().decode(AuthResponse.self, from: data)
        try SessionManager.shared.saveJWT(authResponse.accessToken)
        return authResponse
    }

    // Verify guest session is still valid
    func validateGuestSession(_ token: String) async throws -> Bool {
        var request = URLRequest(url: baseURL.appendingPathComponent("/auth/guest/validate"))
        request.httpMethod = "GET"
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")

        let (_, response) = try await session.data(for: request)
        return (response as? HTTPURLResponse)?.statusCode == 200
    }
}

struct GuestSessionResponse: Codable {
    let accessToken: String
    let expiresIn: Int
    let userId: String
}

enum GuestError: Error {
    case sessionCreationFailed
    case migrationFailed
}
```

---

## Security Best Practices

### Rate Limiting

**Swift Implementation**
```swift
class RateLimitManager {
    private var attempts: [String: [Date]] = [:]
    private let maxAttempts = 5
    private let timeWindow: TimeInterval = 60 * 15 // 15 minutes

    func checkRateLimit(for identifier: String) -> Bool {
        let now = Date()

        if var attemptTimes = attempts[identifier] {
            // Remove old attempts outside time window
            attemptTimes.removeAll { $0.timeIntervalSince(now) < -timeWindow }

            if attemptTimes.count >= maxAttempts {
                return false // Rate limit exceeded
            }

            attemptTimes.append(now)
            attempts[identifier] = attemptTimes
        } else {
            attempts[identifier] = [now]
        }

        return true // Rate limit not exceeded
    }

    func reset(for identifier: String) {
        attempts.removeValue(forKey: identifier)
    }
}
```

### Brute Force Protection

**Swift Implementation**
```swift
class BruteForceProtection {
    private var failedAttempts: [String: [Date]] = [:]
    private let maxFailedAttempts = 5
    private let lockoutDuration: TimeInterval = 15 * 60 // 15 minutes

    func recordFailedAttempt(for username: String) {
        let now = Date()

        if var attempts = failedAttempts[username] {
            attempts.append(now)
            failedAttempts[username] = attempts
        } else {
            failedAttempts[username] = [now]
        }
    }

    func isAccountLocked(username: String) -> Bool {
        guard let attempts = failedAttempts[username] else {
            return false
        }

        let recentAttempts = attempts.filter { Date().timeIntervalSince($0) < lockoutDuration }
        return recentAttempts.count >= maxFailedAttempts
    }

    func clearFailedAttempts(for username: String) {
        failedAttempts.removeValue(forKey: username)
    }

    func getRemainingLockoutTime(for username: String) -> TimeInterval? {
        guard let attempts = failedAttempts[username], !attempts.isEmpty else {
            return nil
        }

        let oldestAttempt = attempts.min() ?? Date()
        let remainingTime = lockoutDuration - Date().timeIntervalSince(oldestAttempt)

        return remainingTime > 0 ? remainingTime : nil
    }
}
```

### Secure Storage Best Practices

**Swift Implementation**
```swift
class SecureStorage {
    // Always use Keychain for sensitive data
    static func storeCredential(_ credential: String, forKey key: String) throws {
        let data = credential.data(using: .utf8)!
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecValueData as String: data,
            kSecAttrAccessible as String: kSecAttrAccessibleWhenPasscodeSetThisDeviceOnly,
            kSecAttrSynchronizable as String: false // Don't sync to iCloud
        ]

        SecItemDelete(query as CFDictionary)
        let status = SecItemAdd(query as CFDictionary, nil)
        guard status == errSecSuccess else { throw StorageError.failed }
    }

    static func retrieveCredential(forKey key: String) -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]

        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)

        guard status == errSecSuccess, let data = result as? Data else {
            return nil
        }

        return String(data: data, encoding: .utf8)
    }

    static func deleteCredential(forKey key: String) throws {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key
        ]

        let status = SecItemDelete(query as CFDictionary)
        guard status == errSecSuccess else { throw StorageError.deletionFailed }
    }
}

enum StorageError: Error {
    case failed
    case deletionFailed
}
```

### HTTPS Pinning

**Swift Implementation**
```swift
import CryptoKit

class CertificatePinningDelegate: NSObject, URLSessionDelegate {
    private let publicKeyHash: String

    init(publicKeyHash: String) {
        self.publicKeyHash = publicKeyHash
    }

    func urlSession(
        _ session: URLSession,
        didReceive challenge: URLAuthenticationChallenge,
        completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void
    ) {
        guard let serverTrust = challenge.protectionSpace.serverTrust,
              SecTrustEvaluateWithError(serverTrust, nil) else {
            completionHandler(.cancelAuthenticationChallenge, nil)
            return
        }

        var secResult = SecTrustResultType.invalid
        let status = SecTrustEvaluate(serverTrust, &secResult)

        guard status == errSecSuccess else {
            completionHandler(.cancelAuthenticationChallenge, nil)
            return
        }

        let certificateCount = SecTrustGetCertificateCount(serverTrust)
        for i in 0..<certificateCount {
            if let certificate = SecTrustGetCertificateAtIndex(serverTrust, i) {
                let key = SecCertificateCopyKey(certificate)
                let keyData = SecKeyCopyExternalRepresentation(key!, nil) as Data?

                if let keyData = keyData {
                    let hash = Data(SHA256.hash(data: keyData))
                    let hashString = hash.base64EncodedString()

                    if hashString == publicKeyHash {
                        completionHandler(.useCredential, URLCredential(trust: serverTrust))
                        return
                    }
                }
            }
        }

        completionHandler(.cancelAuthenticationChallenge, nil)
    }
}
```

---

## Implementation Checklist

- [ ] Implement email/password authentication with secure password hashing
- [ ] Configure OAuth2/OIDC with mandatory PKCE flow
- [ ] Integrate biometric authentication (Face ID/Touch ID on iOS, BiometricPrompt on Android)
- [ ] Implement JWT storage in Keychain (iOS) or Keystore (Android)
- [ ] Add token refresh mechanism with proper expiration handling
- [ ] Configure MFA with TOTP, SMS, or push verification
- [ ] Integrate at least one auth provider (Firebase, Supabase, Auth0, or Cognito)
- [ ] Implement Apple Sign In with proper App Store requirements
- [ ] Implement Google Sign In for both iOS and Android
- [ ] Add account linking functionality
- [ ] Implement password reset and email verification flows
- [ ] Support guest-to-auth user migration
- [ ] Apply rate limiting and brute force protection
- [ ] Use Keychain/Keystore for sensitive data storage
- [ ] Implement HTTPS certificate pinning
- [ ] Test all auth flows thoroughly on real devices
- [ ] Document auth setup and configuration for team
