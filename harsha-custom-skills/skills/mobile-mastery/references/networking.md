# Mobile Networking Reference Guide

Complete production-ready networking implementations for iOS, Android, React Native, and Flutter covering HTTP clients, REST APIs, GraphQL, WebSockets, security, caching, and advanced patterns.

---

## Table of Contents

1. HTTP Clients & Setup
2. REST API Patterns
3. GraphQL Clients
4. WebSocket Implementation
5. Certificate Pinning & Security
6. Image Loading & Caching
7. Caching Strategies
8. Background Downloads
9. Retry Logic & Exponential Backoff
10. Network Reachability Monitoring
11. Request Cancellation & Debouncing
12. Multipart Uploads
13. Network Debugging Tools

---

## 1. HTTP Clients & Setup

### iOS (Swift) - URLSession with Interceptors

```swift
import Foundation

// MARK: - Network Manager
class NetworkManager {
    static let shared = NetworkManager()
    private let session: URLSession

    init() {
        let config = URLSessionConfiguration.default
        config.waitsForConnectivity = true
        config.timeoutIntervalForRequest = 30
        config.timeoutIntervalForResource = 300
        config.requestCachePolicy = .reloadIgnoringLocalCacheData
        config.httpMaximumConnectionsPerHost = 6

        self.session = URLSession(configuration: config,
                                  delegate: URLSessionDelegate(),
                                  delegateQueue: .main)
    }

    func request<T: Decodable>(
        _ endpoint: Endpoint,
        responseType: T.Type
    ) async throws -> T {
        let request = try buildRequest(endpoint)
        let (data, response) = try await session.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw NetworkError.invalidResponse
        }

        try validateResponse(httpResponse)
        return try JSONDecoder().decode(T.self, from: data)
    }

    private func buildRequest(_ endpoint: Endpoint) throws -> URLRequest {
        var request = URLRequest(url: endpoint.url)
        request.httpMethod = endpoint.method.rawValue
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("gzip", forHTTPHeaderField: "Accept-Encoding")

        // Add custom headers
        endpoint.headers.forEach { key, value in
            request.setValue(value, forHTTPHeaderField: key)
        }

        if let body = endpoint.body {
            request.httpBody = try JSONSerialization.data(withJSONObject: body)
        }

        return request
    }

    private func validateResponse(_ response: HTTPURLResponse) throws {
        switch response.statusCode {
        case 200...299:
            return
        case 400:
            throw NetworkError.badRequest
        case 401:
            throw NetworkError.unauthorized
        case 404:
            throw NetworkError.notFound
        case 500...599:
            throw NetworkError.serverError
        default:
            throw NetworkError.unknown
        }
    }
}

// MARK: - Endpoint Protocol
protocol Endpoint {
    var baseURL: URL { get }
    var path: String { get }
    var method: HTTPMethod { get }
    var headers: [String: String] { get }
    var body: [String: Any]? { get }
}

extension Endpoint {
    var url: URL {
        baseURL.appendingPathComponent(path)
    }

    var headers: [String: String] {
        [:]
    }

    var body: [String: Any]? {
        nil
    }
}

enum HTTPMethod: String {
    case get = "GET"
    case post = "POST"
    case put = "PUT"
    case patch = "PATCH"
    case delete = "DELETE"
}

enum NetworkError: Error {
    case badRequest
    case unauthorized
    case notFound
    case serverError
    case invalidResponse
    case decodingError
    case unknown
}
```

### Android (Kotlin) - OkHttp with Retrofit

```kotlin
import okhttp3.*
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

// MARK: - Network Module
object NetworkModule {
    private const val BASE_URL = "https://api.example.com/"

    fun provideOkHttpClient(interceptor: AuthInterceptor): OkHttpClient {
        val logging = HttpLoggingInterceptor().apply {
            level = if (BuildConfig.DEBUG) {
                HttpLoggingInterceptor.Level.BODY
            } else {
                HttpLoggingInterceptor.Level.NONE
            }
        }

        return OkHttpClient.Builder()
            .addInterceptor(interceptor)
            .addInterceptor(logging)
            .retryOnConnectionFailure(true)
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .writeTimeout(30, TimeUnit.SECONDS)
            .connectionPool(ConnectionPool(8, 5, TimeUnit.MINUTES))
            .build()
    }

    fun provideRetrofit(okHttpClient: OkHttpClient): Retrofit {
        return Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }
}

// MARK: - Auth Interceptor
class AuthInterceptor(private val tokenManager: TokenManager) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val originalRequest = chain.request()
        val token = tokenManager.getAccessToken()

        val authenticatedRequest = originalRequest.newBuilder()
            .header("Authorization", "Bearer $token")
            .header("Accept-Encoding", "gzip")
            .header("Content-Type", "application/json")
            .build()

        return try {
            chain.proceed(authenticatedRequest)
        } catch (e: Exception) {
            if (originalRequest.header("X-Retry-Count")?.toIntOrNull() ?: 0 < 3) {
                val retryCount = (originalRequest.header("X-Retry-Count")?.toIntOrNull() ?: 0) + 1
                val retryRequest = authenticatedRequest.newBuilder()
                    .header("X-Retry-Count", retryCount.toString())
                    .build()
                chain.proceed(retryRequest)
            } else {
                throw e
            }
        }
    }
}

// MARK: - API Service
interface ApiService {
    @GET("users/{id}")
    suspend fun getUser(@Path("id") id: String): Response<UserDto>

    @POST("posts")
    suspend fun createPost(@Body request: CreatePostRequest): Response<PostDto>

    @GET("posts")
    suspend fun getPosts(
        @Query("page") page: Int,
        @Query("limit") limit: Int = 20
    ): Response<PagedResponse<PostDto>>
}

data class PagedResponse<T>(
    val data: List<T>,
    val page: Int,
    val total: Int,
    val hasMore: Boolean
)
```

### React Native - Axios with Interceptors

```javascript
import axios, { AxiosInstance } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// MARK: - Network Service
class NetworkService {
  private axiosInstance: AxiosInstance;

  constructor() {
    this.axiosInstance = axios.create({
      baseURL: 'https://api.example.com',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
        'Accept-Encoding': 'gzip',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request Interceptor
    this.axiosInstance.interceptors.request.use(
      async (config) => {
        const token = await AsyncStorage.getItem('accessToken');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        config.headers['X-Request-ID'] = this.generateRequestId();
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response Interceptor
    this.axiosInstance.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          const newToken = await this.refreshToken();
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          return this.axiosInstance(originalRequest);
        }

        return Promise.reject(error);
      }
    );
  }

  async get<T>(url: string, params?: Record<string, any>): Promise<T> {
    const { data } = await this.axiosInstance.get<T>(url, { params });
    return data;
  }

  async post<T>(url: string, payload: any): Promise<T> {
    const { data } = await this.axiosInstance.post<T>(url, payload);
    return data;
  }

  private async refreshToken(): Promise<string> {
    // Implementation for token refresh
    return '';
  }

  private generateRequestId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }
}

export const networkService = new NetworkService();
```

### Flutter - Dio with Interceptors

```dart
import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class NetworkService {
  late Dio _dio;
  final _secureStorage = const FlutterSecureStorage();

  NetworkService() {
    _dio = Dio(BaseOptions(
      baseUrl: 'https://api.example.com',
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 30),
      headers: {
        'Content-Type': 'application/json',
        'Accept-Encoding': 'gzip',
      },
    ));

    _setupInterceptors();
  }

  void _setupInterceptors() {
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          final token = await _secureStorage.read(key: 'accessToken');
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          options.headers['X-Request-ID'] = _generateRequestId();
          return handler.next(options);
        },
        onResponse: (response, handler) {
          return handler.next(response);
        },
        onError: (error, handler) async {
          if (error.response?.statusCode == 401) {
            final newToken = await _refreshToken();
            if (newToken != null) {
              error.requestOptions.headers['Authorization'] = 'Bearer $newToken';
              return handler.resolve(await _dio.fetch(error.requestOptions));
            }
          }
          return handler.next(error);
        },
      ),
    );
  }

  Future<T> get<T>(
    String path, {
    Map<String, dynamic>? queryParameters,
  }) async {
    final response = await _dio.get(
      path,
      queryParameters: queryParameters,
    );
    return response.data as T;
  }

  Future<T> post<T>(String path, dynamic data) async {
    final response = await _dio.post(path, data: data);
    return response.data as T;
  }

  Future<String?> _refreshToken() async {
    // Implementation for token refresh
    return null;
  }

  String _generateRequestId() => '${DateTime.now().millisecondsSinceEpoch}-${UniqueKey()}';
}
```

---

## 2. REST API Patterns

### Pagination Pattern

```swift
// iOS
struct PaginatedRequest {
    let page: Int
    let pageSize: Int
    let sortBy: String?
    let sortOrder: SortOrder

    var queryParameters: [String: Any] {
        var params: [String: Any] = [
            "page": page,
            "page_size": pageSize
        ]
        if let sortBy = sortBy {
            params["sort_by"] = sortBy
            params["sort_order"] = sortOrder.rawValue
        }
        return params
    }
}

enum SortOrder: String {
    case ascending = "asc"
    case descending = "desc"
}

struct PaginatedResponse<T: Decodable>: Decodable {
    let data: [T]
    let pagination: PaginationMeta
}

struct PaginationMeta: Decodable {
    let currentPage: Int
    let pageSize: Int
    let totalItems: Int
    let totalPages: Int

    var hasNextPage: Bool { currentPage < totalPages }
}
```

```kotlin
// Android
data class PaginatedRequest(
    val page: Int = 1,
    val pageSize: Int = 20,
    val sortBy: String? = null,
    val sortOrder: SortOrder = SortOrder.ASC
)

enum class SortOrder {
    ASC, DESC
}

data class PaginatedResponse<T>(
    val data: List<T>,
    val pagination: PaginationMeta
)

data class PaginationMeta(
    val currentPage: Int,
    val pageSize: Int,
    val totalItems: Int,
    val totalPages: Int
) {
    val hasNextPage: Boolean get() = currentPage < totalPages
}
```

### Error Response Mapping

```swift
// iOS
struct APIError: Decodable, Error {
    let code: String
    let message: String
    let details: [String: String]?

    enum CodingKeys: String, CodingKey {
        case code = "error_code"
        case message = "error_message"
        case details = "error_details"
    }
}

extension NetworkManager {
    func handleResponse<T: Decodable>(
        data: Data,
        response: HTTPURLResponse,
        as type: T.Type
    ) throws -> T {
        do {
            return try JSONDecoder().decode(T.self, from: data)
        } catch {
            if let apiError = try? JSONDecoder().decode(APIError.self, from: data) {
                throw apiError
            }
            throw NetworkError.decodingError
        }
    }
}
```

```kotlin
// Android
data class APIError(
    @SerializedName("error_code")
    val code: String,
    @SerializedName("error_message")
    val message: String,
    @SerializedName("error_details")
    val details: Map<String, String>? = null
) : Exception(message)

class ApiErrorConverter : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val response = chain.proceed(chain.request())

        if (!response.isSuccessful) {
            val errorBody = response.peekBody(Long.MAX_VALUE).string()
            val apiError = Gson().fromJson(errorBody, APIError::class.java)
            throw apiError
        }
        return response
    }
}
```

---

## 3. GraphQL Clients

### iOS - Apollo Client

```swift
import Apollo

class ApolloManager {
    static let shared = ApolloManager()
    let client: ApolloClient

    init() {
        let cache = InMemoryNormalizedCache()
        let store = ApolloStore(cache: cache)

        let customNetworkTransport = RequestChainNetworkTransport(
            interceptorProvider: DefaultInterceptorProvider(store: store),
            endpointURL: URL(string: "https://api.example.com/graphql")!
        )

        self.client = ApolloClient(networkTransport: customNetworkTransport, store: store)
    }

    func fetchUser(id: String) async throws -> User {
        return try await client.fetch(query: GetUserQuery(id: id))
            .data?.user.fragments.userFragment
            .map { User(fragment: $0) }
            ?? User.default
    }

    func subscribeToMessages() -> AnyPublisher<Message, Error> {
        Future { promise in
            self.client.subscribe(
                subscription: OnMessageSubscription(),
                resultHandler: { result in
                    switch result {
                    case .success(let data):
                        if let message = data.data?.onMessage {
                            promise(.success(Message(data: message)))
                        }
                    case .failure(let error):
                        promise(.failure(error))
                    }
                }
            )
        }
        .eraseToAnyPublisher()
    }
}
```

### Android - Apollo Client

```kotlin
import com.apollographql.apollo3.ApolloClient
import com.apollographql.apollo3.network.okHttpClient
import okhttp3.OkHttpClient

class ApolloManager(private val okHttpClient: OkHttpClient) {
    val client = ApolloClient.Builder()
        .serverUrl("https://api.example.com/graphql")
        .okHttpClient(okHttpClient)
        .build()

    suspend fun fetchUser(id: String): User {
        val response = client.query(GetUserQuery(id = id)).execute()
        return response.data?.user?.let { User(it) }
            ?: throw Exception("User not found")
    }

    fun subscribeToMessages(): Flow<Message> = flow {
        client.subscription(OnMessageSubscription())
            .toFlow()
            .collect { response ->
                response.data?.onMessage?.let { emit(Message(it)) }
            }
    }
}
```

### React Native & Flutter - urql

```javascript
// React Native
import { createClient } from 'urql';

export const graphqlClient = createClient({
  url: 'https://api.example.com/graphql',
  fetchOptions: () => ({
    headers: {
      authorization: `Bearer ${getToken()}`,
    },
  }),
  exchanges: [cacheExchange, fetchExchange],
});

// Usage with hooks
const [result] = useQuery({
  query: GetUserQuery,
  variables: { id: '123' },
  pause: false,
});
```

```dart
// Flutter
import 'package:graphql/client.dart';

class GraphQLService {
  late GraphQLClient _client;

  GraphQLService() {
    final httpLink = HttpLink('https://api.example.com/graphql');
    final authLink = AuthLink(
      getToken: () async => 'Bearer ${await _getToken()}',
    );

    _client = GraphQLClient(
      link: authLink.concat(httpLink),
      cache: GraphQLCache(),
    );
  }

  Future<T> query<T>(
    DocumentNode document, {
    Map<String, dynamic>? variables,
  }) async {
    final result = await _client.query(
      QueryOptions(
        document: document,
        variables: variables ?? {},
      ),
    );
    return result.data as T;
  }
}
```

---

## 4. WebSocket Implementation

### iOS (Swift)

```swift
class WebSocketManager: NSObject, URLSessionWebSocketDelegate {
    static let shared = WebSocketManager()
    private var webSocket: URLSessionWebSocket?
    var onMessageReceived: ((String) -> Void)?
    var onConnectionStatusChanged: ((Bool) -> Void)?

    func connect(url: URL) {
        let urlSession = URLSession(configuration: .default, delegate: self, delegateQueue: .main)
        webSocket = urlSession.webSocketTask(with: url)
        webSocket?.resume()
        receiveMessage()
        onConnectionStatusChanged?(true)
    }

    func disconnect() {
        webSocket?.cancel(with: .goingAway, reason: nil)
        onConnectionStatusChanged?(false)
    }

    func send(_ message: String) {
        let message = URLSessionWebSocketTask.Message.string(message)
        webSocket?.send(message) { error in
            if let error = error {
                print("WebSocket send error: \(error)")
            }
        }
    }

    private func receiveMessage() {
        webSocket?.receive { [weak self] result in
            switch result {
            case .success(let message):
                switch message {
                case .string(let text):
                    self?.onMessageReceived?(text)
                case .data(let data):
                    if let text = String(data: data, encoding: .utf8) {
                        self?.onMessageReceived?(text)
                    }
                @unknown default:
                    break
                }
                self?.receiveMessage()
            case .failure(let error):
                print("WebSocket receive error: \(error)")
            }
        }
    }
}
```

### Android (Kotlin)

```kotlin
import okhttp3.WebSocket
import okhttp3.WebSocketListener
import okhttp3.Request

class WebSocketManager(private val okHttpClient: OkHttpClient) {
    private var webSocket: WebSocket? = null
    var onMessageReceived: ((String) -> Unit)? = null
    var onConnectionStatusChanged: ((Boolean) -> Unit)? = null

    fun connect(url: String) {
        val request = Request.Builder()
            .url(url)
            .header("Authorization", "Bearer ${getToken()}")
            .build()

        webSocket = okHttpClient.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {
                onConnectionStatusChanged?.invoke(true)
            }

            override fun onMessage(webSocket: WebSocket, text: String) {
                onMessageReceived?.invoke(text)
            }

            override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
                onConnectionStatusChanged?.invoke(false)
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                onConnectionStatusChanged?.invoke(false)
            }
        })
    }

    fun send(message: String) {
        webSocket?.send(message)
    }

    fun disconnect() {
        webSocket?.close(1000, "Disconnecting")
    }
}
```

### React Native

```javascript
class WebSocketClient {
  constructor() {
    this.ws = null;
    this.url = 'wss://api.example.com/ws';
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
  }

  connect() {
    this.ws = new WebSocket(this.url);

    this.ws.onopen = () => {
      this.reconnectAttempts = 0;
      this.onConnectionStatusChanged?.(true);
    };

    this.ws.onmessage = (e) => {
      this.onMessageReceived?.(e.data);
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    this.ws.onclose = () => {
      this.onConnectionStatusChanged?.(false);
      this.attemptReconnect();
    };
  }

  send(message) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    }
  }

  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = Math.pow(2, this.reconnectAttempts) * 1000;
      setTimeout(() => this.connect(), delay);
    }
  }

  disconnect() {
    this.ws?.close();
  }
}
```

---

## 5. Certificate Pinning & SSL/TLS

### iOS (Swift)

```swift
class CertificatePinningDelegate: NSObject, URLSessionDelegate {
    func urlSession(
        _ session: URLSession,
        didReceive challenge: URLAuthenticationChallenge,
        completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void
    ) {
        guard let serverTrust = challenge.protectionSpace.serverTrust else {
            completionHandler(.cancelAuthenticationChallenge, nil)
            return
        }

        // Validate certificate
        var secResult = SecTrustResultType.invalid
        let status = SecTrustEvaluate(serverTrust, &secResult)

        guard status == errSecSuccess else {
            completionHandler(.cancelAuthenticationChallenge, nil)
            return
        }

        // Pin certificate
        let certificatePath = Bundle.main.path(forResource: "api.example.com", ofType: "cer")!
        let certificateData = NSData(contentsOfFile: certificatePath)!
        let certificate = SecCertificateCreateWithData(nil, certificateData as CFData)!

        let pinningPolicy = SecPolicyCreateSSL(true, challenge.protectionSpace.host as CFString)
        SecTrustSetPolicies(serverTrust, pinningPolicy)
        SecTrustSetAnchorCertificates(serverTrust, [certificate] as CFArray)

        SecTrustEvaluate(serverTrust, &secResult)

        if secResult == .unspecified || secResult == .proceed {
            completionHandler(.useCredential, URLCredential(trust: serverTrust))
        } else {
            completionHandler(.cancelAuthenticationChallenge, nil)
        }
    }
}
```

### Android (Kotlin)

```kotlin
import javax.net.ssl.HttpsURLConnection
import okhttp3.CertificatePinner

fun createPinnedOkHttpClient(): OkHttpClient {
    val certificatePinner = CertificatePinner.Builder()
        .add("api.example.com", "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
        .add("api.example.com", "sha256/BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=")
        .build()

    return OkHttpClient.Builder()
        .certificatePinner(certificatePinner)
        .build()
}

// Get certificate SHA256 with openssl:
// openssl s_client -connect api.example.com:443 < /dev/null | \
// openssl x509 -outform DER | \
// openssl dgst -sha256 -binary | openssl enc -base64
```

### React Native & Flutter

```javascript
// React Native with axios
import axios from 'axios';
import { default as https } from 'https';
import fs from 'fs';

const cert = fs.readFileSync('./api.example.com.pem');
const httpsAgent = new https.Agent({
  ca: [cert],
});

export const secureAxios = axios.create({
  httpsAgent,
});
```

```dart
// Flutter
import 'package:flutter/services.dart' show rootBundle;
import 'dart:io';

Future<SecurityContext> getSecurityContext() async {
  final sslCert = await rootBundle.load('assets/api.example.com.pem');
  final context = SecurityContext.defaultContext
    ..setTrustedCertificatesBytes(sslCert.buffer.asUint8List());
  return context;
}

class PinnedHttpClient extends HttpClient {
  PinnedHttpClient._internal(SecurityContext context) : super(context: context);

  factory PinnedHttpClient() {
    return PinnedHttpClient._internal(SecurityContext.defaultContext);
  }
}
```

---

## 6. Image Loading & Caching

### iOS (Swift) - Kingfisher

```swift
import Kingfisher

class ImageLoader {
    static func loadImage(
        from url: URL,
        placeholder: UIImage? = nil,
        completion: @escaping (UIImage?) -> Void
    ) {
        let processor = DownsamplingImageProcessor(size: CGSize(width: 300, height: 300))
            |> RoundCornerImageProcessor(cornerRadius: 10)

        var options: KingfisherOptionsInfo = [
            .processor(processor),
            .cacheOriginalImage,
            .cacheMemoryOnly(false),
            .scaleFactor(UIScreen.main.scale)
        ]

        // Add certificate pinning if needed
        let modifier = AnyModifier { request in
            var req = request
            req.setValue("gzip", forHTTPHeaderField: "Accept-Encoding")
            return req
        }
        options.append(.requestModifier(modifier))

        KingfisherManager.shared.retrieveImage(
            with: url,
            options: options,
            completionHandler: { result in
                switch result {
                case .success(let imageResult):
                    completion(imageResult.image)
                case .failure:
                    completion(placeholder)
                }
            }
        )
    }

    static func clearImageCache() {
        ImageCache.default.clearMemoryCache()
        ImageCache.default.clearDiskCache()
    }
}
```

### Android (Kotlin) - Coil

```kotlin
import coil.compose.AsyncImage
import coil.ImageLoader
import coil.disk.DiskCache
import coil.memory.MemoryCache
import coil.request.ImageRequest

fun createImageLoader(context: Context): ImageLoader {
    return ImageLoader.Builder(context)
        .memoryCache {
            MemoryCache.Builder(context)
                .maxSizePercent(0.25)
                .build()
        }
        .diskCache {
            DiskCache.Builder()
                .directory(File(context.cacheDir, "image_cache"))
                .maxSizeBytes(50 * 1024 * 1024) // 50 MB
                .build()
        }
        .httpClient {
            OkHttpClient.Builder()
                .cache(Cache(File(context.cacheDir, "http_cache"), 50 * 1024 * 1024))
                .build()
        }
        .build()
}

// Usage in Compose
@Composable
fun LoadImage(url: String) {
    AsyncImage(
        model = ImageRequest.Builder(LocalContext.current)
            .data(url)
            .size(300, 300)
            .scale(Scale.FILL)
            .build(),
        contentDescription = "Image",
        contentScale = ContentScale.Crop,
        modifier = Modifier
            .size(300.dp)
            .clip(RoundedCornerShape(10.dp))
    )
}
```

### React Native - FastImage

```javascript
import FastImage from 'react-native-fast-image';

export const CachedImage = ({ uri, style }) => (
  <FastImage
    source={{
      uri,
      priority: FastImage.priority.normal,
      cache: FastImage.cacheControl.immutable,
    }}
    style={style}
    onLoad={() => console.log('Image loaded')}
    onError={(error) => console.error('Image load error:', error)}
  />
);

// Clear cache
FastImage.clearMemoryCache().then(() => console.log('Memory cache cleared'));
FastImage.clearDiskCache().then(() => console.log('Disk cache cleared'));
```

### Flutter - CachedNetworkImage

```dart
import 'package:cached_network_image/cached_network_image.dart';

class CachedImageWidget extends StatelessWidget {
  final String imageUrl;

  const CachedImageWidget({required this.imageUrl});

  @override
  Widget build(BuildContext context) {
    return CachedNetworkImage(
      imageUrl: imageUrl,
      imageBuilder: (context, imageProvider) => Container(
        decoration: BoxDecoration(
          image: DecorationImage(
            image: imageProvider,
            fit: BoxFit.cover,
          ),
          borderRadius: BorderRadius.circular(10),
        ),
      ),
      placeholder: (context, url) => const Shimmer(
        child: SizedBox(width: 300, height: 300),
      ),
      errorWidget: (context, url, error) => const Icon(Icons.error),
      cacheManager: CacheManager(
        Config(
          'image_cache',
          stalePeriod: const Duration(days: 30),
          maxNrOfCacheObjects: 100,
          diskFileService: FileFetcherService(httpClient: http.Client()),
        ),
      ),
    );
  }
}
```

---

## 7. Caching Strategies

### ETag & Cache-Control Pattern

```swift
// iOS
class HTTPCacheManager {
    static let shared = HTTPCacheManager()
    private let urlCache = URLCache(
        memoryCapacity: 50 * 1024 * 1024,
        diskCapacity: 500 * 1024 * 1024,
        diskPath: "http_cache"
    )

    func request<T: Decodable>(
        _ endpoint: Endpoint,
        responseType: T.Type
    ) async throws -> T {
        var urlRequest = URLRequest(url: endpoint.url)
        urlRequest.cachePolicy = .returnCacheDataElseLoad

        // Check cached response
        if let cachedResponse = urlCache.cachedResponse(for: urlRequest),
           let etag = cachedResponse.response.value(forHTTPHeaderField: "ETag") {
            urlRequest.setValue(etag, forHTTPHeaderField: "If-None-Match")
        }

        let (data, response) = try await URLSession.shared.data(for: urlRequest)

        if let httpResponse = response as? HTTPURLResponse {
            if httpResponse.statusCode == 304 {
                // Use cached data
                if let cachedData = urlCache.cachedResponse(for: urlRequest)?.data {
                    return try JSONDecoder().decode(T.self, from: cachedData)
                }
            }

            // Cache new response
            if let cacheControl = httpResponse.value(forHTTPHeaderField: "Cache-Control") {
                let response = CachedURLResponse(response: httpResponse, data: data)
                urlCache.storeCachedResponse(response, for: urlRequest)
            }
        }

        return try JSONDecoder().decode(T.self, from: data)
    }
}
```

```kotlin
// Android
class CacheInterceptor : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request()

        // Add cache headers
        val cacheRequest = request.newBuilder()
            .header("Cache-Control", "public, max-age=3600")
            .build()

        var response = chain.proceed(cacheRequest)

        // Handle ETag
        val etag = response.header("ETag")
        if (response.code == 200 && etag != null) {
            // Store ETag for next request
            storeETag(request.url.toString(), etag)
        }

        if (response.code == 304) {
            // Return cached response
            response = getCachedResponse(request.url.toString()) ?: response
        }

        return response
    }
}
```

---

## 8. Background Downloads

### iOS

```swift
class BackgroundDownloadManager: NSObject, URLSessionDownloadDelegate {
    static let shared = BackgroundDownloadManager()
    private var backgroundSession: URLSession!
    var onDownloadProgress: ((Double) -> Void)?
    var onDownloadComplete: ((URL?) -> Void)?

    override init() {
        super.init()
        let config = URLSessionConfiguration.background(withIdentifier: "com.example.downloads")
        config.isDiscretionary = false
        backgroundSession = URLSession(configuration: config, delegate: self, delegateQueue: nil)
    }

    func startDownload(from url: URL, fileName: String) {
        var request = URLRequest(url: url)
        request.timeoutInterval = 600
        backgroundSession.downloadTask(with: request).resume()
    }

    func urlSession(
        _ session: URLSession,
        downloadTask: URLSessionDownloadTask,
        didFinishDownloadingTo location: URL
    ) {
        let fileManager = FileManager.default
        let documentsURL = fileManager.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let savedURL = documentsURL.appendingPathComponent("downloads").appendingPathComponent("file.pdf")

        try? fileManager.moveItem(at: location, to: savedURL)
        DispatchQueue.main.async {
            self.onDownloadComplete?(savedURL)
        }
    }

    func urlSession(
        _ session: URLSession,
        downloadTask: URLSessionDownloadTask,
        didWriteData bytesWritten: Int64,
        totalBytesWritten: Int64,
        totalBytesExpectedToWrite: Int64
    ) {
        let progress = Double(totalBytesWritten) / Double(totalBytesExpectedToWrite)
        DispatchQueue.main.async {
            self.onDownloadProgress?(progress)
        }
    }
}
```

### Android

```kotlin
import android.app.DownloadManager
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Environment

class BackgroundDownloadManager(private val context: Context) {
    private val downloadManager = context.getSystemService(Context.DOWNLOAD_SERVICE) as DownloadManager

    fun startDownload(url: String, fileName: String): Long {
        val uri = Uri.parse(url)
        val request = DownloadManager.Request(uri)
            .setTitle(fileName)
            .setDescription("Downloading...")
            .setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
            .setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, fileName)
            .setAllowedNetworkTypes(DownloadManager.Request.NETWORK_WIFI or DownloadManager.Request.NETWORK_MOBILE)

        return downloadManager.enqueue(request)
    }
}

class DownloadCompleteReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context?, intent: Intent?) {
        if (intent?.action == DownloadManager.ACTION_DOWNLOAD_COMPLETE) {
            val downloadId = intent.getLongExtra(DownloadManager.EXTRA_DOWNLOAD_ID, -1L)
            // Handle download completion
        }
    }
}
```

---

## 9. Retry with Exponential Backoff

### Multi-platform Pattern

```swift
// iOS
func requestWithRetry<T: Decodable>(
    _ endpoint: Endpoint,
    maxRetries: Int = 3,
    baseDelay: TimeInterval = 1.0
) async throws -> T {
    var lastError: Error?

    for attempt in 0..<maxRetries {
        do {
            return try await NetworkManager.shared.request(endpoint, responseType: T.self)
        } catch let error as NetworkError {
            lastError = error

            switch error {
            case .serverError, .unknown:
                let delay = baseDelay * pow(2, Double(attempt))
                try await Task.sleep(nanoseconds: UInt64(delay * 1_000_000_000))
                continue
            default:
                throw error
            }
        }
    }

    throw lastError ?? NetworkError.unknown
}
```

```kotlin
// Android
suspend inline fun <reified T> requestWithRetry(
    maxRetries: Int = 3,
    baseDelay: Long = 1000,
    crossinline request: suspend () -> T
): T {
    var lastError: Exception? = null

    repeat(maxRetries) { attempt ->
        try {
            return request()
        } catch (e: Exception) {
            lastError = e
            if (attempt < maxRetries - 1) {
                val delay = baseDelay * (2.0.pow(attempt.toDouble()).toLong())
                delay(delay)
            }
        }
    }

    throw lastError ?: Exception("Max retries exceeded")
}
```

```javascript
// React Native
async function requestWithRetry(
  requestFn,
  maxRetries = 3,
  baseDelay = 1000
) {
  let lastError;

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await requestFn();
    } catch (error) {
      lastError = error;
      if (attempt < maxRetries - 1) {
        const delay = baseDelay * Math.pow(2, attempt);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }

  throw lastError;
}
```

---

## 10. Network Reachability Monitoring

### iOS (Swift)

```swift
import Network

class NetworkMonitor: ObservableObject {
    @Published var isConnected = true
    @Published var connectionType: NWInterface.InterfaceType = .wifi

    private let monitor = NWPathMonitor()
    private let queue = DispatchQueue(label: "NetworkMonitor")

    func startMonitoring() {
        monitor.pathUpdateHandler = { [weak self] path in
            DispatchQueue.main.async {
                self?.isConnected = path.status == .satisfied
                self?.connectionType = path.usesInterfaceType(.wifi) ? .wifi : .cellular
            }
        }
        monitor.start(queue: queue)
    }

    func stopMonitoring() {
        monitor.cancel()
    }
}
```

### Android (Kotlin)

```kotlin
import android.content.Context
import android.net.ConnectivityManager
import android.net.Network
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

class NetworkMonitor(context: Context) {
    private val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager

    private val _isConnected = MutableStateFlow(isNetworkAvailable())
    val isConnected: StateFlow<Boolean> = _isConnected

    init {
        val networkCallback = object : ConnectivityManager.NetworkCallback() {
            override fun onAvailable(network: Network) {
                _isConnected.value = true
            }

            override fun onLost(network: Network) {
                _isConnected.value = isNetworkAvailable()
            }
        }
        connectivityManager.registerDefaultNetworkCallback(networkCallback)
    }

    private fun isNetworkAvailable(): Boolean {
        return connectivityManager.activeNetwork != null
    }
}
```

### React Native

```javascript
import { useEffect, useState } from 'react';
import NetInfo from '@react-native-community/netinfo';

export function useNetworkStatus() {
  const [isConnected, setIsConnected] = useState(true);
  const [connectionType, setConnectionType] = useState('unknown');

  useEffect(() => {
    const unsubscribe = NetInfo.addEventListener(state => {
      setIsConnected(state.isConnected);
      setConnectionType(state.type);
    });

    return unsubscribe;
  }, []);

  return { isConnected, connectionType };
}
```

---

## 11. Request Cancellation & Debouncing

### iOS (Swift)

```swift
class RequestManager {
    private var activeTasks: [String: URLSessionTask] = [:]

    func cancelRequest(withKey key: String) {
        activeTasks[key]?.cancel()
        activeTasks.removeValue(forKey: key)
    }

    func debounce<T: Decodable>(
        key: String,
        delay: TimeInterval = 0.5,
        endpoint: Endpoint,
        responseType: T.Type,
        completion: @escaping (Result<T, Error>) -> Void
    ) {
        // Cancel previous request with same key
        cancelRequest(withKey: key)

        let deadline = DispatchTime.now() + delay
        DispatchQueue.main.asyncAfter(deadline: deadline) { [weak self] in
            let task = URLSession.shared.dataTask(with: endpoint.url) { data, response, error in
                if let data = data {
                    do {
                        let result = try JSONDecoder().decode(T.self, from: data)
                        completion(.success(result))
                    } catch {
                        completion(.failure(error))
                    }
                } else {
                    completion(.failure(error ?? NetworkError.unknown))
                }
            }

            self?.activeTasks[key] = task
            task.resume()
        }
    }
}
```

### Android (Kotlin)

```kotlin
import kotlinx.coroutines.*

class RequestManager {
    private val scope = CoroutineScope(Dispatchers.IO + Job())
    private val activeJobs: MutableMap<String, Job> = mutableMapOf()

    fun <T> debounceRequest(
        key: String,
        delay: Long = 500,
        request: suspend () -> T,
        onResult: (Result<T>) -> Unit
    ) {
        // Cancel previous request
        activeJobs[key]?.cancel()

        activeJobs[key] = scope.launch {
            delay(delay)
            try {
                val result = request()
                onResult(Result.success(result))
            } catch (e: Exception) {
                onResult(Result.failure(e))
            }
        }
    }

    fun cancelRequest(key: String) {
        activeJobs[key]?.cancel()
        activeJobs.remove(key)
    }
}
```

### React Native

```javascript
class DebouncedRequestManager {
  constructor() {
    this.pendingRequests = new Map();
    this.abortControllers = new Map();
  }

  async debounceRequest(key, fn, delay = 500) {
    // Cancel previous request
    if (this.abortControllers.has(key)) {
      this.abortControllers.get(key).abort();
    }

    // Cancel pending debounce
    if (this.pendingRequests.has(key)) {
      clearTimeout(this.pendingRequests.get(key));
    }

    const abortController = new AbortController();
    this.abortControllers.set(key, abortController);

    return new Promise((resolve, reject) => {
      const timeoutId = setTimeout(async () => {
        try {
          const result = await fn(abortController.signal);
          resolve(result);
        } catch (error) {
          reject(error);
        } finally {
          this.abortControllers.delete(key);
          this.pendingRequests.delete(key);
        }
      }, delay);

      this.pendingRequests.set(key, timeoutId);
    });
  }
}
```

---

## 12. Multipart Uploads

### iOS (Swift)

```swift
func uploadMultipart(
    url: URL,
    parameters: [String: String],
    fileURL: URL
) async throws {
    var request = URLRequest(url: url)
    request.httpMethod = "POST"

    let boundary = UUID().uuidString
    request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")

    var body = Data()

    // Add form fields
    for (key, value) in parameters {
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"\(key)\"\r\n\r\n".data(using: .utf8)!)
        body.append("\(value)\r\n".data(using: .utf8)!)
    }

    // Add file
    let fileData = try Data(contentsOf: fileURL)
    let fileName = fileURL.lastPathComponent
    body.append("--\(boundary)\r\n".data(using: .utf8)!)
    body.append("Content-Disposition: form-data; name=\"file\"; filename=\"\(fileName)\"\r\n".data(using: .utf8)!)
    body.append("Content-Type: application/octet-stream\r\n\r\n".data(using: .utf8)!)
    body.append(fileData)
    body.append("\r\n--\(boundary)--\r\n".data(using: .utf8)!)

    request.httpBody = body

    let (_, response) = try await URLSession.shared.data(for: request)
    guard (response as? HTTPURLResponse)?.statusCode == 200 else {
        throw NetworkError.serverError
    }
}
```

### Android (Kotlin)

```kotlin
fun uploadMultipart(
    url: String,
    parameters: Map<String, String>,
    fileUri: Uri
) {
    val requestBody = MultipartBody.Builder()
        .setType(MultipartBody.FORM)
        .apply {
            parameters.forEach { (key, value) ->
                addFormDataPart(key, value)
            }
        }
        .addFormDataPart(
            "file",
            "upload.bin",
            RequestBody.create("application/octet-stream".toMediaType(), fileUri.toFile())
        )
        .build()

    val request = Request.Builder()
        .url(url)
        .post(requestBody)
        .build()

    httpClient.newCall(request).enqueue(object : Callback {
        override fun onResponse(call: Call, response: Response) {
            if (response.isSuccessful) {
                // Handle success
            }
        }

        override fun onFailure(call: Call, e: IOException) {
            // Handle error
        }
    })
}
```

### React Native

```javascript
async function uploadMultipart(url, parameters, filePath) {
  const formData = new FormData();

  Object.entries(parameters).forEach(([key, value]) => {
    formData.append(key, value);
  });

  formData.append('file', {
    uri: filePath,
    type: 'application/octet-stream',
    name: 'upload.bin',
  });

  const response = await fetch(url, {
    method: 'POST',
    body: formData,
    headers: {
      'Accept': 'application/json',
    },
  });

  return response.json();
}
```

---

## 13. Network Debugging Tools

### Charles Proxy Integration

```swift
// iOS - Enable Charles Proxy in debug builds
#if DEBUG
import Foundation

class CharlesProxyHelper {
    static func setupProxyIfAvailable() {
        let proxyHost = "127.0.0.1"
        let proxyPort = 8888

        let proxyDict: [AnyHashable: Any] = [
            kCFNetworkProxiesHTTPEnable: true,
            kCFNetworkProxiesHTTPProxy: proxyHost,
            kCFNetworkProxiesHTTPPort: proxyPort,
            kCFNetworkProxiesHTTPSEnable: true,
            kCFNetworkProxiesHTTPSProxy: proxyHost,
            kCFNetworkProxiesHTTPSPort: proxyPort,
        ]

        let config = URLSessionConfiguration.default
        config.connectionProxyDictionary = proxyDict
    }
}
#endif
```

```kotlin
// Android - Proxyman Integration
object NetworkDebugging {
    fun setupProxyIfDebug(context: Context): OkHttpClient.Builder {
        return OkHttpClient.Builder().apply {
            if (BuildConfig.DEBUG) {
                addNetworkInterceptor(HttpLoggingInterceptor().apply {
                    level = HttpLoggingInterceptor.Level.BODY
                })
            }
        }
    }
}
```

### Logging Interceptor Pattern

```swift
// iOS - Request/Response Logging
class LoggingInterceptor: URLProtocol {
    override class func canInit(with request: URLRequest) -> Bool {
        return true
    }

    override class func canonicalRequest(for request: URLRequest) -> URLRequest {
        return request
    }

    override func startLoading() {
        let request = self.request
        print("→ REQUEST: \(request.httpMethod ?? "GET") \(request.url?.absoluteString ?? "")")
        print("→ HEADERS: \(request.allHTTPHeaderFields ?? [:])")

        URLSession.shared.dataTask(with: request) { data, response, error in
            if let response = response as? HTTPURLResponse {
                print("← RESPONSE: \(response.statusCode)")
                if let data = data, let json = try? JSONSerialization.jsonObject(with: data) {
                    print("← BODY: \(json)")
                }
            }

            if let error = error {
                print("← ERROR: \(error.localizedDescription)")
            }
        }.resume()
    }

    override func stopLoading() {}
}
```

```kotlin
// Android - Comprehensive Request Logging
class DetailedLoggingInterceptor : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request()
        val startTime = System.currentTimeMillis()

        println("→ REQUEST: ${request.method} ${request.url}")
        println("→ HEADERS: ${request.headers}")
        request.body?.let {
            val copy = Buffer()
            it.writeTo(copy)
            println("→ BODY: ${copy.readUtf8()}")
        }

        val response = try {
            chain.proceed(request)
        } catch (e: Exception) {
            println("← ERROR: ${e.message}")
            throw e
        }

        val duration = System.currentTimeMillis() - startTime
        println("← RESPONSE: ${response.code} (${duration}ms)")
        println("← HEADERS: ${response.headers}")
        println("← BODY: ${response.peekBody(Long.MAX_VALUE).string()}")

        return response
    }
}
```

---

## Best Practices Summary

- Use async/await for modern, readable asynchronous code
- Implement proper error handling with custom error types
- Add request/response logging only in debug builds
- Use certificate pinning for sensitive API endpoints
- Implement exponential backoff for automatic retries
- Cache responses appropriately using ETags and Cache-Control headers
- Monitor network connectivity before making requests
- Use image caching libraries to reduce bandwidth usage
- Implement request debouncing for search/filter operations
- Always provide user feedback for long-running operations
- Test on real devices with various network conditions
- Use network debugging tools (Charles Proxy, Proxyman) during development

---

*Last updated: 2026-03-03*
*Compatible with iOS 15+, Android 8+, React Native 0.68+, Flutter 3.0+*
