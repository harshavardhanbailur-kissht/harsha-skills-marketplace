# Push Notifications Reference Guide

## Table of Contents

- [1. Push Architecture Overview](#1-push-architecture-overview)
- [2. iOS Push Notifications](#2-ios-push-notifications)
- [3. Android Push Notifications](#3-android-push-notifications)
- [4. React Native Push Notifications](#4-react-native-push-notifications)
- [5. Flutter Push Notifications](#5-flutter-push-notifications)
- [6. Background Processing](#6-background-processing)
- [7. Silent/Data Notifications](#7-silentdata-notifications)
- [8. Local Notifications and Scheduling](#8-local-notifications-and-scheduling)
- [9. Notification Grouping and Summary](#9-notification-grouping-and-summary)
- [10. Permission Best Practices](#10-permission-best-practices)
- [11. Analytics and Tracking](#11-analytics-and-tracking)

## 1. Push Architecture Overview

### APNs vs FCM Comparison

| Feature | APNs | FCM |
|---------|------|-----|
| Platform | iOS/macOS/watchOS | Android/iOS/Web |
| Connection | Persistent socket | HTTP/2 |
| Delivery Guarantee | Best effort | Best effort |
| Priority Levels | 10 (default), 1 (background) | High, Normal |
| Certificate Type | p8 (recommended) | Service account JSON |
| TTL Support | Yes | Yes |
| Custom Payload | Yes (up to 4KB) | Yes |

### Delivery Flow Architecture

```
[Backend Server]
    |
    +---> [APNs Service] ---> [APNs Feedback Service]
    |         |
    |         v
    |     [iOS Device]
    |
    +---> [FCM Service]
          |
          v
      [Android Device] / [iOS Device]

Feedback Loop:
- Device tokens expire or become invalid
- Services notify backend via feedback mechanisms
- Backend updates token database
```

## 2. iOS Push Notifications

### UNUserNotificationCenter Setup

```swift
import UserNotifications

// Request user permission
func requestNotificationPermission() {
    UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound, .badge]) { granted, error in
        if granted {
            DispatchQueue.main.async {
                UIApplication.shared.registerForRemoteNotifications()
            }
        }
        if let error = error {
            print("Permission error: \(error.localizedDescription)")
        }
    }
}

// Handle remote notification registration
func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
    UNUserNotificationCenter.current().delegate = self
    return true
}

func application(_ application: UIApplication, didRegisterForRemoteNotificationsWithDeviceToken deviceToken: Data) {
    let token = deviceToken.map { String(format: "%02.2hhx", $0) }.joined()
    print("Device Token: \(token)")
    // Send token to backend server
    UserDefaults.standard.set(token, forKey: "apnsToken")
}

func application(_ application: UIApplication, didFailToRegisterForRemoteNotificationsWithError error: Error) {
    print("Failed to register for remote notifications: \(error)")
}
```

### Notification Delegate & Handling

```swift
extension AppDelegate: UNUserNotificationCenterDelegate {

    // Handle notification when app is in foreground
    func userNotificationCenter(_ center: UNUserNotificationCenter,
                              willPresent notification: UNNotification,
                              withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void) {
        let userInfo = notification.request.content.userInfo

        if #available(iOS 14.0, *) {
            completionHandler([.banner, .sound, .badge])
        } else {
            completionHandler([.alert, .sound, .badge])
        }
    }

    // Handle user interaction with notification
    func userNotificationCenter(_ center: UNUserNotificationCenter,
                              didReceive response: UNNotificationResponse,
                              withCompletionHandler completionHandler: @escaping () -> Void) {
        let userInfo = response.notification.request.content.userInfo
        let actionIdentifier = response.actionIdentifier

        if actionIdentifier == UNNotificationDefaultActionIdentifier {
            // User tapped notification
            handleNotificationTap(userInfo)
        } else if actionIdentifier == "REPLY_ACTION" {
            if let textResponse = response as? UNTextInputNotificationResponse {
                handleReplyAction(userInfo, text: textResponse.userText)
            }
        }

        completionHandler()
    }

    private func handleNotificationTap(_ userInfo: [AnyHashable: Any]) {
        if let deepLink = userInfo["deepLink"] as? String {
            // Navigate to screen based on deepLink
        }
    }

    private func handleReplyAction(_ userInfo: [AnyHashable: Any], text: String) {
        // Process user's reply text
    }
}
```

### Notification Categories and Actions

```swift
func setupNotificationCategories() {
    // Define actions
    let replyAction = UNTextInputNotificationAction(
        identifier: "REPLY_ACTION",
        title: "Reply",
        options: [],
        textInputButtonTitle: "Send",
        textInputPlaceholder: "Type your reply..."
    )

    let deleteAction = UNNotificationAction(
        identifier: "DELETE_ACTION",
        title: "Delete",
        options: .destructive
    )

    let archiveAction = UNNotificationAction(
        identifier: "ARCHIVE_ACTION",
        title: "Archive",
        options: []
    )

    // Group actions into category
    let messageCategory = UNNotificationCategory(
        identifier: "MESSAGE_CATEGORY",
        actions: [replyAction, deleteAction, archiveAction],
        intentIdentifiers: [],
        options: .customDismissAction
    )

    // Set categories
    UNUserNotificationCenter.current().setNotificationCategories([messageCategory])
}
```

### Rich Notifications with Attachments

```swift
class NotificationAttachmentHandler {
    static func createAttachmentIdentifier(for urlString: String) -> String {
        return UUID().uuidString
    }

    static func downloadAttachment(from urlString: String, completion: @escaping (UNNotificationAttachment?) -> Void) {
        guard let url = URL(string: urlString) else {
            completion(nil)
            return
        }

        let task = URLSession.shared.downloadTask(with: url) { tempURL, response, error in
            guard let tempURL = tempURL else {
                completion(nil)
                return
            }

            do {
                let identifier = createAttachmentIdentifier(for: urlString)
                let fileExtension = URL(fileURLWithPath: urlString).pathExtension
                let temporaryDirectory = NSTemporaryDirectory()
                let temporaryFilePath = temporaryDirectory + identifier + "." + fileExtension
                let localURL = URL(fileURLWithPath: temporaryFilePath)

                try FileManager.default.moveItem(at: tempURL, to: localURL)

                let attachment = try UNNotificationAttachment(
                    identifier: identifier,
                    url: localURL,
                    options: [UNNotificationAttachmentOptionsThumbnailClippingRectKey: CGRect(x: 0.1, y: 0.1, width: 0.8, height: 0.8)]
                )
                completion(attachment)
            } catch {
                completion(nil)
            }
        }
        task.resume()
    }
}

// Usage in notification extension
func didReceive(_ request: UNNotificationRequest, withContentHandler contentHandler: @escaping (UNNotificationContent) -> Void) {
    let content = request.content.mutableCopy() as! UNMutableNotificationContent

    if let imageURL = content.userInfo["imageUrl"] as? String {
        NotificationAttachmentHandler.downloadAttachment(from: imageURL) { attachment in
            if let attachment = attachment {
                content.attachments = [attachment]
            }
            contentHandler(content)
        }
    } else {
        contentHandler(content)
    }
}
```

### Notification Service Extension

```swift
import UserNotifications

class NotificationService: UNNotificationServiceExtension {
    var contentHandler: ((UNNotificationContent) -> Void)?
    var bestAttemptContent: UNMutableNotificationContent?

    override func didReceive(_ request: UNNotificationRequest, withContentHandler contentHandler: @escaping (UNNotificationContent) -> Void) {
        self.contentHandler = contentHandler
        bestAttemptContent = (request.content.mutableCopy() as? UNMutableNotificationContent)

        if let bestAttemptContent = bestAttemptContent {
            // Modify notification content
            bestAttemptContent.title = "Modified: \(bestAttemptContent.title)"

            // Download and attach media
            if let imageUrlString = request.content.userInfo["imageUrl"] as? String,
               let imageUrl = URL(string: imageUrlString) {
                downloadImage(from: imageUrl) { attachment in
                    if let attachment = attachment {
                        bestAttemptContent.attachments = [attachment]
                    }
                    contentHandler(bestAttemptContent)
                }
            } else {
                contentHandler(bestAttemptContent)
            }
        }
    }

    override func serviceExtensionTimeWillExpire() {
        if let bestAttemptContent = bestAttemptContent {
            contentHandler?(bestAttemptContent)
        }
    }

    private func downloadImage(from url: URL, completion: @escaping (UNNotificationAttachment?) -> Void) {
        URLSession.shared.downloadTask(with: url) { tempURL, _, error in
            guard let tempURL = tempURL, error == nil else {
                completion(nil)
                return
            }

            do {
                let fileName = UUID().uuidString
                let documentDirectory = FileManager.default.temporaryDirectory
                let fileURL = documentDirectory.appendingPathComponent(fileName)
                try FileManager.default.moveItem(at: tempURL, to: fileURL)

                let attachment = try UNNotificationAttachment(identifier: fileName, url: fileURL, options: nil)
                completion(attachment)
            } catch {
                completion(nil)
            }
        }.resume()
    }
}
```

### Provisional Authorization

```swift
// Request provisional authorization (notifications appear silently in Notification Center)
func requestProvisionalAuthorization() {
    UNUserNotificationCenter.current().requestAuthorization(options: .provisional) { granted, error in
        if granted {
            DispatchQueue.main.async {
                UIApplication.shared.registerForRemoteNotifications()
            }
        }
    }
}
```

### Live Activities (iOS 16.1+)

```swift
import ActivityKit

struct DeliveryActivityAttributes: ActivityAttributes {
    public struct ContentState: Codable, Hashable {
        var driverName: String
        var estimatedMinutes: Int
        var location: String
    }

    var orderId: String
}

// Start Live Activity
func startLiveActivity() {
    let attributes = DeliveryActivityAttributes(orderId: "12345")
    let initialState = DeliveryActivityAttributes.ContentState(
        driverName: "John Doe",
        estimatedMinutes: 15,
        location: "Main St"
    )

    let activity = try? Activity<DeliveryActivityAttributes>.request(
        attributes: attributes,
        content: .init(state: initialState, staleDate: nil),
        pushType: .token
    )

    if let pushTokenData = activity?.pushTokenUpdates.first.pushToken {
        let pushToken = pushTokenData.map { String(format: "%02x", $0) }.joined()
        // Send pushToken to backend
    }
}

// Update Live Activity via push
func updateLiveActivityViaPush(pushToken: String) {
    let payload: [String: Any] = [
        "aps": [
            "alert": [
                "title": "Order Update",
                "body": "Driver is 10 minutes away"
            ],
            "sound": "default",
            "badge": 1,
            "custom-key": "custom-value"
        ],
        "activity-update": [
            "driver-name": "Jane Smith",
            "estimated-minutes": 10,
            "location": "Oak Ave"
        ]
    ]
}
```

### Focus Filters (iOS 15.1+)

```swift
let focusFilter = UNNotificationSettings()
// Notifications can be configured to respect Focus modes
// This is handled by system - focus filters applied automatically
```

## 3. Android Push Notifications

### Firebase Cloud Messaging Setup

```kotlin
import com.google.firebase.messaging.FirebaseMessaging
import com.google.firebase.messaging.FirebaseMessagingService
import com.google.firebase.messaging.RemoteMessage

class MyFirebaseMessagingService : FirebaseMessagingService() {

    override fun onNewToken(token: String) {
        super.onNewToken(token)
        // Send token to backend
        sendTokenToServer(token)
    }

    override fun onMessageReceived(remoteMessage: RemoteMessage) {
        super.onMessageReceived(remoteMessage)

        // Check if message contains data and notification
        if (remoteMessage.data.isNotEmpty()) {
            val data = remoteMessage.data
            val title = data["title"] ?: ""
            val body = data["body"] ?: ""
            showNotification(title, body, data)
        }

        if (remoteMessage.notification != null) {
            val notification = remoteMessage.notification
            showNotification(
                notification?.title ?: "",
                notification?.body ?: "",
                remoteMessage.data
            )
        }
    }

    private fun sendTokenToServer(token: String) {
        // Upload token to backend
        Log.d("FCM", "Token: $token")
    }
}
```

### Notification Channels

```kotlin
import android.app.NotificationChannel
import android.app.NotificationManager
import android.os.Build
import androidx.core.app.NotificationCompat

fun createNotificationChannels(context: Context) {
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
        val notificationManager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

        // High priority channel
        val highPriorityChannel = NotificationChannel(
            "HIGH_PRIORITY",
            "High Priority Notifications",
            NotificationManager.IMPORTANCE_HIGH
        ).apply {
            description = "Important notifications requiring immediate attention"
            enableVibration(true)
            enableLights(true)
            lightColor = Color.RED
        }

        // Default channel
        val defaultChannel = NotificationChannel(
            "DEFAULT",
            "Default Notifications",
            NotificationManager.IMPORTANCE_DEFAULT
        ).apply {
            description = "Standard notifications"
        }

        // Low priority channel
        val lowPriorityChannel = NotificationChannel(
            "LOW_PRIORITY",
            "Low Priority Notifications",
            NotificationManager.IMPORTANCE_LOW
        ).apply {
            description = "Background notifications"
        }

        notificationManager.createNotificationChannels(
            listOf(highPriorityChannel, defaultChannel, lowPriorityChannel)
        )
    }
}
```

### BigText and BigPicture Styles

```kotlin
import androidx.core.app.NotificationCompat

fun showBigTextNotification(context: Context, title: String, message: String, channelId: String) {
    val notificationId = 1

    val notification = NotificationCompat.Builder(context, channelId)
        .setSmallIcon(R.drawable.ic_notification)
        .setContentTitle(title)
        .setContentText(message)
        .setStyle(NotificationCompat.BigTextStyle()
            .bigText("This is a much longer text that will be shown when the user expands the notification. It can contain multiple lines and detailed information about the notification."))
        .setAutoCancel(true)
        .build()

    val notificationManager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
    notificationManager.notify(notificationId, notification)
}

fun showBigPictureNotification(context: Context, title: String, imageUrl: String, channelId: String) {
    val notificationId = 2

    // Download bitmap from URL (in production, use Glide/Picasso)
    val bitmap = downloadBitmap(imageUrl)

    val notification = NotificationCompat.Builder(context, channelId)
        .setSmallIcon(R.drawable.ic_notification)
        .setContentTitle(title)
        .setContentText("Large image notification")
        .setStyle(NotificationCompat.BigPictureStyle()
            .bigPicture(bitmap)
            .bigLargeIcon(null))
        .setLargeIcon(bitmap)
        .setAutoCancel(true)
        .build()

    val notificationManager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
    notificationManager.notify(notificationId, notification)
}

fun showMessagingStyleNotification(context: Context, channelId: String) {
    val notificationId = 3

    val messagingStyle = NotificationCompat.MessagingStyle("You")
        .addMessage("Hello!", System.currentTimeMillis() - 1000, Person.Builder().setName("Alice").build())
        .addMessage("How are you?", System.currentTimeMillis(), Person.Builder().setName("Alice").build())

    val notification = NotificationCompat.Builder(context, channelId)
        .setSmallIcon(R.drawable.ic_notification)
        .setStyle(messagingStyle)
        .setAutoCancel(true)
        .build()

    val notificationManager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
    notificationManager.notify(notificationId, notification)
}

private fun downloadBitmap(url: String): Bitmap? {
    return try {
        val connection = URL(url).openConnection() as HttpURLConnection
        connection.doInput = true
        connection.connect()
        BitmapFactory.decodeStream(connection.inputStream)
    } catch (e: Exception) {
        null
    }
}
```

### Notification Actions

```kotlin
import android.app.PendingIntent
import android.content.Intent

fun showNotificationWithActions(context: Context, channelId: String) {
    val notificationId = 4

    // Create intents for actions
    val replyIntent = Intent(context, ReplyReceiver::class.java)
    val replyPendingIntent = PendingIntent.getBroadcast(
        context,
        1,
        replyIntent,
        PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
    )

    val deleteIntent = Intent(context, DeleteReceiver::class.java)
    val deletePendingIntent = PendingIntent.getBroadcast(
        context,
        2,
        deleteIntent,
        PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
    )

    val notification = NotificationCompat.Builder(context, channelId)
        .setSmallIcon(R.drawable.ic_notification)
        .setContentTitle("Message")
        .setContentText("You have a new message")
        .addAction(
            R.drawable.ic_reply,
            "Reply",
            replyPendingIntent
        )
        .addAction(
            R.drawable.ic_delete,
            "Delete",
            deletePendingIntent
        )
        .setAutoCancel(true)
        .build()

    val notificationManager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
    notificationManager.notify(notificationId, notification)
}
```

### Notification Bubbles (Android 11+)

```kotlin
import android.app.PendingIntent
import androidx.core.app.NotificationCompat

fun showBubbleNotification(context: Context, channelId: String) {
    val bubbleIntent = Intent(context, BubbleActivity::class.java)
    val bubblePendingIntent = PendingIntent.getActivity(
        context,
        0,
        bubbleIntent,
        PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_MUTABLE
    )

    val notification = NotificationCompat.Builder(context, channelId)
        .setSmallIcon(R.drawable.ic_notification)
        .setContentTitle("Chat")
        .setContentText("New message from Alice")
        .setBubbleMetadata(
            NotificationCompat.BubbleMetadata.Builder(bubblePendingIntent)
                .setDesiredHeight(600)
                .setIcon(R.drawable.ic_bubble_icon)
                .setAutoExpandBubble(true)
                .setSuppressNotification(false)
                .build()
        )
        .build()

    val notificationManager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
    notificationManager.notify(5, notification)
}
```

### Foreground Service Notifications

```kotlin
import android.app.Service
import android.content.Intent
import android.os.IBinder
import androidx.core.app.NotificationCompat

class ForegroundService : Service() {

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        createForegroundNotification()
        // Do background work
        return START_STICKY
    }

    private fun createForegroundNotification() {
        val notification = NotificationCompat.Builder(this, "SERVICE_CHANNEL")
            .setContentTitle("Background Service")
            .setContentText("Running in background")
            .setSmallIcon(R.drawable.ic_notification)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .setOngoing(true)
            .build()

        startForeground(1, notification)
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
```

## 4. React Native Push Notifications

### Notifee Setup

```javascript
import notifee, { AndroidImportance } from '@notifee/react-native';

// Create notification channel
async function createNotificationChannel() {
  await notifee.createChannel({
    id: 'default',
    name: 'Default Channel',
    importance: AndroidImportance.DEFAULT,
    sound: 'default',
  });
}

// Display local notification
async function displayNotification(title, body) {
  await notifee.displayNotification({
    title,
    body,
    android: {
      channelId: 'default',
      smallIcon: 'icon_0',
      pressAction: {
        id: 'default',
      },
    },
    ios: {
      sound: 'default',
    },
  });
}

// Handle notification press
notifee.onNotificationOpenedApp((notification) => {
  console.log('Notification opened app:', notification);
  // Navigate to screen based on notification data
});

// Handle notification when app killed
notifee.getInitialNotification().then((notification) => {
  if (notification) {
    console.log('App opened from notification:', notification);
  }
});

// Listen to foreground notifications
notifee.onForegroundEvent(({ type, notification }) => {
  console.log('Foreground notification:', notification);
});
```

### Expo Notifications

```javascript
import * as Notifications from 'expo-notifications';

// Configure notification handler
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

// Request permissions
async function registerForPushNotifications() {
  const { status } = await Notifications.requestPermissionsAsync();
  if (status !== 'granted') {
    console.log('Permission not granted');
    return;
  }

  // Get device token
  const token = (await Notifications.getExpoPushTokenAsync()).data;
  console.log('Push token:', token);
  return token;
}

// Schedule local notification
async function scheduleNotification(seconds = 5) {
  await Notifications.scheduleNotificationAsync({
    content: {
      title: 'Scheduled Notification',
      body: 'This notification was scheduled!',
      data: { deepLink: 'app://home' },
    },
    trigger: { seconds },
  });
}

// Listen to notification events
Notifications.addNotificationResponseReceivedListener((response) => {
  console.log('Notification tapped:', response.notification.request.content.data);
});

Notifications.addNotificationReceivedListener((notification) => {
  console.log('Notification received:', notification);
});
```

### Firebase Cloud Messaging (React Native)

```javascript
import messaging from '@react-native-firebase/messaging';

class FCMService {
  register = () => {
    this.checkPermission();
    this.createNotificationListeners();
  };

  checkPermission = async () => {
    const enabled = await messaging().hasPermission();
    if (enabled === messaging.AuthorizationStatus.AUTHORIZED) {
      this.getToken();
    } else if (enabled === messaging.AuthorizationStatus.PROVISIONAL) {
      console.log('Provisional authorization');
    } else {
      this.requestPermission();
    }
  };

  requestPermission = async () => {
    try {
      await messaging().requestPermission();
      this.getToken();
    } catch (error) {
      console.log('Permission rejected', error);
    }
  };

  getToken = async () => {
    const token = await messaging().getToken();
    console.log('FCM Token:', token);
    // Send to backend
  };

  createNotificationListeners = () => {
    // Foreground notification listener
    this.messageListener = messaging().onMessage(async (message) => {
      console.log('Foreground message:', message);
      this.handleForegroundNotification(message);
    });

    // Background/Quit state listener
    messaging().onNotificationOpenedApp((message) => {
      console.log('App opened from notification:', message);
      this.navigateToScreen(message.data);
    });

    // App quit state notification
    messaging()
      .getInitialNotification()
      .then((message) => {
        if (message) {
          console.log('App started from notification:', message);
          this.navigateToScreen(message.data);
        }
      });

    // Token refresh listener
    this.tokenListener = messaging().onTokenRefresh((token) => {
      console.log('New FCM token:', token);
      // Update token on backend
    });
  };

  handleForegroundNotification = (message) => {
    // Use notifee to display notification in foreground
    notifee.displayNotification({
      title: message.notification?.title,
      body: message.notification?.body,
      android: {
        channelId: 'default',
      },
    });
  };

  navigateToScreen = (data) => {
    if (data?.deepLink) {
      // Navigate using deep link
    }
  };

  unRegister = () => {
    this.messageListener();
    this.tokenListener();
  };
}

export default FCMService;
```

## 5. Flutter Push Notifications

### Firebase Cloud Messaging

```dart
import 'package:firebase_messaging/firebase_messaging.dart';

class FirebaseMessagingService {
  final FirebaseMessaging _messaging = FirebaseMessaging.instance;

  Future<void> initializeMessaging() async {
    // Request permission
    NotificationSettings settings = await _messaging.requestPermission(
      alert: true,
      announcement: true,
      badge: true,
      carPlay: false,
      criticalAlert: false,
      provisional: false,
      sound: true,
    );

    if (settings.authorizationStatus == AuthorizationStatus.authorized) {
      print('User granted permission');
    } else if (settings.authorizationStatus == AuthorizationStatus.provisional) {
      print('User granted provisional permission');
    } else {
      print('User declined or has not yet granted permission');
    }

    // Get device token
    String? token = await _messaging.getToken();
    print('FCM Token: $token');

    // Listen to token refresh
    _messaging.onTokenRefresh.listen((newToken) {
      print('Token refreshed: $newToken');
      // Send to backend
    });

    // Handle foreground messages
    FirebaseMessaging.onMessage.listen((RemoteMessage message) {
      print('Foreground message: ${message.notification?.title}');
      _handleForegroundMessage(message);
    });

    // Handle background messages
    FirebaseMessaging.onMessageOpenedApp.listen((RemoteMessage message) {
      print('Message clicked: ${message.data}');
      _navigateToScreen(message.data);
    });

    // Handle message when app is terminated
    RemoteMessage? initialMessage = await _messaging.getInitialMessage();
    if (initialMessage != null) {
      _navigateToScreen(initialMessage.data);
    }
  }

  void _handleForegroundMessage(RemoteMessage message) {
    if (message.notification != null) {
      print('Notification: ${message.notification?.title}');
      print('Body: ${message.notification?.body}');
    }
  }

  void _navigateToScreen(Map<String, dynamic> data) {
    String? deepLink = data['deepLink'];
    if (deepLink != null) {
      // Handle deep link navigation
    }
  }
}

// Background message handler (must be top-level function)
Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  print('Handling background message: ${message.messageId}');
  // Handle background message
}

void main() {
  FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);
  runApp(MyApp());
}
```

### Flutter Local Notifications

```dart
import 'package:flutter_local_notifications/flutter_local_notifications.dart';

class LocalNotificationService {
  static final LocalNotificationService _instance = LocalNotificationService._internal();

  factory LocalNotificationService() {
    return _instance;
  }

  LocalNotificationService._internal();

  final FlutterLocalNotificationsPlugin _flutterLocalNotificationsPlugin =
      FlutterLocalNotificationsPlugin();

  Future<void> initializeNotifications() async {
    const AndroidInitializationSettings initializationSettingsAndroid =
        AndroidInitializationSettings('@mipmap/ic_launcher');

    final DarwinInitializationSettings initializationSettingsIOS =
        DarwinInitializationSettings(
      onDidReceiveLocalNotification: (id, title, body, payload) async {
        // Handle iOS notification
      },
    );

    final InitializationSettings initializationSettings = InitializationSettings(
      android: initializationSettingsAndroid,
      iOS: initializationSettingsIOS,
    );

    await _flutterLocalNotificationsPlugin.initialize(
      initializationSettings,
      onDidReceiveNotificationResponse: (NotificationResponse response) {
        print('Notification clicked: ${response.payload}');
      },
    );

    // Create notification channels for Android
    const AndroidNotificationChannel channel = AndroidNotificationChannel(
      id: 'high_importance_channel',
      name: 'High Importance Notifications',
      description: 'This channel is used for important notifications.',
      importance: Importance.max,
      enableVibration: true,
      playSound: true,
    );

    await _flutterLocalNotificationsPlugin
        .resolvePlatformSpecificImplementation<
            AndroidFlutterLocalNotificationsPlugin>()
        ?.createNotificationChannel(channel);
  }

  Future<void> showSimpleNotification({
    required String title,
    required String body,
  }) async {
    const AndroidNotificationDetails androidPlatformChannelSpecifics =
        AndroidNotificationDetails(
      'high_importance_channel',
      'High Importance Notifications',
      channelDescription: 'This channel is used for important notifications.',
      importance: Importance.max,
      priority: Priority.high,
      showWhen: true,
    );

    const DarwinNotificationDetails iOSPlatformChannelSpecifics =
        DarwinNotificationDetails();

    const NotificationDetails platformChannelSpecifics = NotificationDetails(
      android: androidPlatformChannelSpecifics,
      iOS: iOSPlatformChannelSpecifics,
    );

    await _flutterLocalNotificationsPlugin.show(
      0,
      title,
      body,
      platformChannelSpecifics,
      payload: 'notification_payload',
    );
  }

  Future<void> scheduleNotification({
    required String title,
    required String body,
    required Duration delayDuration,
  }) async {
    const AndroidNotificationDetails androidPlatformChannelSpecifics =
        AndroidNotificationDetails(
      'high_importance_channel',
      'High Importance Notifications',
      channelDescription: 'This channel is used for important notifications.',
    );

    const NotificationDetails platformChannelSpecifics =
        NotificationDetails(android: androidPlatformChannelSpecifics);

    await _flutterLocalNotificationsPlugin.zonedSchedule(
      0,
      title,
      body,
      tz.TZDateTime.now(tz.local).add(delayDuration),
      platformChannelSpecifics,
      androidAllowWhileIdle: true,
      uiLocalNotificationDateInterpretation:
          UILocalNotificationDateInterpretation.absoluteTime,
    );
  }
}
```

## 6. Background Processing

### iOS BGTaskScheduler

```swift
import BackgroundTasks

func scheduleBackgroundTask() {
    let request = BGProcessingTaskRequest(identifier: "com.app.refreshdata")
    request.requiresNetworkConnectivity = true

    do {
        try BGTaskScheduler.shared.submit(request)
    } catch {
        print("Failed to schedule background task: \(error)")
    }
}

func setupBackgroundTaskHandler() {
    BGTaskScheduler.shared.register(forTaskWithIdentifier: "com.app.refreshdata", using: nil) { task in
        let processTask = task as! BGProcessingTask

        handleBackgroundRefresh {
            processTask.setTaskCompleted(success: true)
        }

        // Set expiration handler
        processTask.expirationHandler = {
            processTask.setTaskCompleted(success: false)
        }
    }
}

private func handleBackgroundRefresh(completion: @escaping () -> Void) {
    URLSession.shared.dataTask(with: URL(string: "https://api.example.com/sync")!) { _, _, _ in
        completion()
    }.resume()
}
```

### Android WorkManager

```kotlin
import androidx.work.Worker
import androidx.work.WorkerParameters
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import java.util.concurrent.TimeUnit

class SyncWorker(appContext: Context, params: WorkerParameters) : Worker(appContext, params) {
    override fun doWork(): Result {
        return try {
            // Perform sync work
            syncData()
            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }

    private fun syncData() {
        // Make network request or perform background work
    }
}

fun schedulePeriodicWork(context: Context) {
    val syncRequest = PeriodicWorkRequestBuilder<SyncWorker>(
        15, TimeUnit.MINUTES
    ).build()

    WorkManager.getInstance(context).enqueueUniquePeriodicWork(
        "sync_work",
        ExistingPeriodicWorkPolicy.KEEP,
        syncRequest
    )
}
```

### React Native Headless JS

```javascript
import { AppRegistry } from 'react-native';

const handleBackgroundMessage = async (message) => {
  console.log('Background message:', message);
  // Perform background work
};

AppRegistry.registerHeadlessTask('RNFirebaseBackgroundMessage', () => handleBackgroundMessage);
```

## 7. Silent/Data Notifications

### iOS Silent Push

```swift
// APNs payload with content-available
let payload = """
{
  "aps": {
    "content-available": 1,
    "sound": ""
  },
  "customKey": "customValue"
}
"""

// Handle in delegate
func userNotificationCenter(_ center: UNUserNotificationCenter,
                          willPresent notification: UNNotification,
                          withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void) {
    if notification.request.content.userInfo["content-available"] as? Int == 1 {
        // Silent notification - perform background sync
        completionHandler([])
    }
}
```

### Android Data Messages

```kotlin
override fun onMessageReceived(remoteMessage: RemoteMessage) {
    if (remoteMessage.data.isNotEmpty()) {
        val data = remoteMessage.data
        // Process data silently without showing notification
        performBackgroundSync(data)
    }
}

private fun performBackgroundSync(data: Map<String, String>) {
    // Sync data without UI
    val workRequest = OneTimeWorkRequestBuilder<SyncWorker>()
        .setInputData(Data.Builder().putAll(data).build())
        .build()

    WorkManager.getInstance(context).enqueueUniqueWork("sync", ExistingWorkPolicy.KEEP, workRequest)
}
```

## 8. Local Notifications and Scheduling

### iOS Local Notifications

```swift
func scheduleLocalNotification(title: String, body: String, seconds: TimeInterval) {
    let content = UNMutableNotificationContent()
    content.title = title
    content.body = body
    content.sound = .default
    content.badge = NSNumber(value: UIApplication.shared.applicationIconBadgeNumber + 1)

    // Add attachment
    if let url = Bundle.main.url(forResource: "notification", withExtension: "jpg") {
        let attachment = try? UNNotificationAttachment(identifier: "image", url: url)
        if let attachment = attachment {
            content.attachments = [attachment]
        }
    }

    let trigger = UNTimeIntervalNotificationTrigger(timeInterval: seconds, repeats: false)
    let request = UNNotificationRequest(identifier: UUID().uuidString, content: content, trigger: trigger)

    UNUserNotificationCenter.current().add(request) { error in
        if let error = error {
            print("Error scheduling notification: \(error)")
        }
    }
}

func scheduleRepeatingNotification(title: String, body: String, interval: TimeInterval) {
    let content = UNMutableNotificationContent()
    content.title = title
    content.body = body

    let trigger = UNTimeIntervalNotificationTrigger(timeInterval: interval, repeats: true)
    let request = UNNotificationRequest(identifier: "repeating", content: content, trigger: trigger)

    UNUserNotificationCenter.current().add(request)
}

func scheduleCalendarNotification(title: String, body: String, hour: Int, minute: Int) {
    let content = UNMutableNotificationContent()
    content.title = title
    content.body = body

    var dateComponents = DateComponents()
    dateComponents.hour = hour
    dateComponents.minute = minute

    let trigger = UNCalendarNotificationTrigger(dateMatching: dateComponents, repeats: true)
    let request = UNNotificationRequest(identifier: "daily", content: content, trigger: trigger)

    UNUserNotificationCenter.current().add(request)
}
```

### Android Local Notifications

```kotlin
fun showDelayedNotification(context: Context, title: String, body: String, delaySeconds: Long) {
    val data = Data.Builder()
        .putString("title", title)
        .putString("body", body)
        .build()

    val notificationRequest = OneTimeWorkRequestBuilder<NotificationWorker>()
        .setInitialDelay(delaySeconds, TimeUnit.SECONDS)
        .setInputData(data)
        .build()

    WorkManager.getInstance(context).enqueueUniqueWork(
        "notification",
        ExistingWorkPolicy.KEEP,
        notificationRequest
    )
}

fun showScheduledNotification(context: Context, title: String, body: String, delayMinutes: Long) {
    val data = Data.Builder()
        .putString("title", title)
        .putString("body", body)
        .build()

    val notificationRequest = OneTimeWorkRequestBuilder<NotificationWorker>()
        .setInitialDelay(delayMinutes, TimeUnit.MINUTES)
        .setInputData(data)
        .build()

    WorkManager.getInstance(context).enqueueUniqueWork(
        "scheduled_notification",
        ExistingWorkPolicy.REPLACE,
        notificationRequest
    )
}
```

## 9. Notification Grouping and Summary

### iOS Notification Grouping

```swift
func createGroupedNotifications() {
    let content1 = UNMutableNotificationContent()
    content1.title = "Message 1"
    content1.body = "From Alice"
    content1.threadIdentifier = "message_thread"
    content1.summaryArgument = "2 messages"

    let content2 = UNMutableNotificationContent()
    content2.title = "Message 2"
    content2.body = "From Bob"
    content2.threadIdentifier = "message_thread"
    content2.summaryArgument = "2 messages"

    let trigger = UNTimeIntervalNotificationTrigger(timeInterval: 1, repeats: false)

    UNUserNotificationCenter.current().add(
        UNNotificationRequest(identifier: "msg1", content: content1, trigger: trigger)
    )
    UNUserNotificationCenter.current().add(
        UNNotificationRequest(identifier: "msg2", content: content2, trigger: trigger)
    )
}
```

### Android Notification Grouping

```kotlin
fun showGroupedNotification(context: Context, channelId: String, groupKey: String, messageId: Int, message: String) {
    val notification = NotificationCompat.Builder(context, channelId)
        .setSmallIcon(R.drawable.ic_notification)
        .setContentTitle("Message $messageId")
        .setContentText(message)
        .setGroup(groupKey)
        .setGroupAlertBehavior(NotificationCompat.GROUP_ALERT_SUMMARY)
        .setAutoCancel(true)
        .build()

    NotificationManagerCompat.from(context).notify(messageId, notification)
}

fun showGroupSummary(context: Context, channelId: String, groupKey: String) {
    val summaryNotification = NotificationCompat.Builder(context, channelId)
        .setSmallIcon(R.drawable.ic_notification)
        .setStyle(NotificationCompat.InboxStyle()
            .setSummaryText("3 messages"))
        .setGroup(groupKey)
        .setGroupSummary(true)
        .setAutoCancel(true)
        .build()

    NotificationManagerCompat.from(context).notify(0, summaryNotification)
}
```

## 10. Permission Best Practices

### Permission Request Timing

```swift
// Request after user action
func requestPermissionAfterUserAction() {
    // Show educational prompt first
    showPermissionEducationDialog {
        UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound, .badge]) { granted, error in
            if granted {
                DispatchQueue.main.async {
                    UIApplication.shared.registerForRemoteNotifications()
                }
            }
        }
    }
}

// Check current permission status
func checkNotificationStatus() {
    UNUserNotificationCenter.current().getNotificationSettings { settings in
        switch settings.authorizationStatus {
        case .authorized:
            print("Notifications authorized")
        case .provisional:
            print("Provisional authorization")
        case .denied:
            print("Notifications denied")
        case .notDetermined:
            print("Not yet requested")
        case .ephemeral:
            print("Ephemeral authorization")
        @unknown default:
            break
        }
    }
}
```

### Re-engagement Strategy

```swift
func showNotificationPromptOptimally() {
    let userDefaults = UserDefaults.standard
    let lastPromptDate = userDefaults.object(forKey: "lastNotificationPrompt") as? Date

    // Only ask if 7 days have passed
    if lastPromptDate == nil || Date().timeIntervalSince(lastPromptDate ?? Date()) > 7 * 24 * 3600 {
        // Show educational UI first
        showNotificationBenefit {
            UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound, .badge]) { _, _ in }
            userDefaults.set(Date(), forKey: "lastNotificationPrompt")
        }
    }
}
```

### Android Permission Request

```kotlin
import android.Manifest
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import android.content.pm.PackageManager

fun requestNotificationPermission(activity: Activity) {
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
        if (ContextCompat.checkSelfPermission(
            activity,
            Manifest.permission.POST_NOTIFICATIONS
        ) != PackageManager.PERMISSION_GRANTED
        ) {
            ActivityCompat.requestPermissions(
                activity,
                arrayOf(Manifest.permission.POST_NOTIFICATIONS),
                NOTIFICATION_PERMISSION_CODE
            )
        }
    }
}

override fun onRequestPermissionsResult(
    requestCode: Int,
    permissions: Array<String>,
    grantResults: IntArray
) {
    super.onRequestPermissionsResult(requestCode, permissions, grantResults)

    if (requestCode == NOTIFICATION_PERMISSION_CODE) {
        if (grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
            // Permission granted
        }
    }
}
```

## 11. Analytics and Tracking

### iOS Analytics

```swift
import os.log

class NotificationAnalytics {
    static let logger = os.log(subsystem: "com.app.notifications", category: "Analytics")

    static func trackNotificationDelivered(notificationId: String, campaignId: String) {
        os_log("Notification delivered: %@", log: logger, type: .info, notificationId)

        // Send to analytics backend
        let payload = [
            "event": "notification_delivered",
            "notification_id": notificationId,
            "campaign_id": campaignId,
            "timestamp": ISO8601DateFormatter().string(from: Date())
        ]

        sendAnalyticsEvent(payload)
    }

    static func trackNotificationOpened(notificationId: String) {
        os_log("Notification opened: %@", log: logger, type: .info, notificationId)

        let payload = [
            "event": "notification_opened",
            "notification_id": notificationId,
            "timestamp": ISO8601DateFormatter().string(from: Date())
        ]

        sendAnalyticsEvent(payload)
    }

    static func trackNotificationAction(notificationId: String, action: String) {
        os_log("Action taken: %@", log: logger, type: .info, action)

        let payload = [
            "event": "notification_action",
            "notification_id": notificationId,
            "action": action,
            "timestamp": ISO8601DateFormatter().string(from: Date())
        ]

        sendAnalyticsEvent(payload)
    }

    private static func sendAnalyticsEvent(_ payload: [String: String]) {
        var request = URLRequest(url: URL(string: "https://api.example.com/analytics/notification")!)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try? JSONSerialization.data(withJSONObject: payload)

        URLSession.shared.dataTask(with: request).resume()
    }
}
```

### Android Analytics

```kotlin
import android.util.Log

class NotificationAnalytics(private val context: Context) {
    companion object {
        private const val TAG = "NotificationAnalytics"
        private const val ANALYTICS_URL = "https://api.example.com/analytics/notification"
    }

    fun trackNotificationDelivered(notificationId: String, campaignId: String) {
        Log.d(TAG, "Notification delivered: $notificationId")

        val payload = mapOf(
            "event" to "notification_delivered",
            "notification_id" to notificationId,
            "campaign_id" to campaignId,
            "timestamp" to System.currentTimeMillis()
        )

        sendAnalyticsEvent(payload)
    }

    fun trackNotificationOpened(notificationId: String) {
        Log.d(TAG, "Notification opened: $notificationId")

        val payload = mapOf(
            "event" to "notification_opened",
            "notification_id" to notificationId,
            "timestamp" to System.currentTimeMillis()
        )

        sendAnalyticsEvent(payload)
    }

    fun trackNotificationAction(notificationId: String, action: String) {
        Log.d(TAG, "Action taken: $action")

        val payload = mapOf(
            "event" to "notification_action",
            "notification_id" to notificationId,
            "action" to action,
            "timestamp" to System.currentTimeMillis()
        )

        sendAnalyticsEvent(payload)
    }

    private fun sendAnalyticsEvent(payload: Map<String, Any>) {
        Thread {
            try {
                val json = JSONObject(payload).toString()
                val url = URL(ANALYTICS_URL)
                val connection = url.openConnection() as HttpURLConnection
                connection.requestMethod = "POST"
                connection.setRequestProperty("Content-Type", "application/json")
                connection.doOutput = true

                connection.outputStream.bufferedWriter().use { it.write(json) }
                connection.inputStream.close()
            } catch (e: Exception) {
                Log.e(TAG, "Error sending analytics", e)
            }
        }.start()
    }
}
```

### React Native Analytics

```javascript
import analytics from '@react-native-firebase/analytics';

class NotificationAnalytics {
  static async trackNotificationDelivered(notificationId, campaignId) {
    try {
      await analytics().logEvent('notification_delivered', {
        notification_id: notificationId,
        campaign_id: campaignId,
        timestamp: new Date().toISOString(),
      });
    } catch (error) {
      console.log('Analytics error:', error);
    }
  }

  static async trackNotificationOpened(notificationId) {
    try {
      await analytics().logEvent('notification_opened', {
        notification_id: notificationId,
        timestamp: new Date().toISOString(),
      });
    } catch (error) {
      console.log('Analytics error:', error);
    }
  }

  static async trackNotificationAction(notificationId, action) {
    try {
      await analytics().logEvent('notification_action', {
        notification_id: notificationId,
        action: action,
        timestamp: new Date().toISOString(),
      });
    } catch (error) {
      console.log('Analytics error:', error);
    }
  }
}

export default NotificationAnalytics;
```

## Summary

This comprehensive guide covers:
- Complete push notification architecture for both iOS and Android
- Platform-specific implementations with code examples
- Cross-platform solutions using React Native and Flutter
- Background processing and silent notifications
- Local notification scheduling
- Permission handling and re-engagement strategies
- Analytics tracking for notification performance

Each section includes production-ready code that can be integrated into your mobile applications.
