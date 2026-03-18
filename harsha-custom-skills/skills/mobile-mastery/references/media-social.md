# Media & Social Features in Mobile Apps

Comprehensive guide to implementing audio, video, camera, social sharing, and real-time messaging features in iOS and Android applications.

## Table of Contents
- [1. Audio Playback](#1-audio-playback)
- [2. Video Playback](#2-video-playback)
- [3. Camera Capture & Recording](#3-camera-capture--recording)
- [4. Social Sharing](#4-social-sharing)
- [5. In-App Chat - Stream SDK & Firebase](#5-in-app-chat---stream-sdk--firebase)
- [6. Real-time Features - Presence & Typing Indicators](#6-real-time-features---presence--typing-indicators)
- [7. User-Generated Content & Moderation](#7-user-generated-content--moderation)
- [8. Image & Video Compression](#8-image--video-compression)
- [9. Media Caching Strategies](#9-media-caching-strategies)
- [10. Streaming Protocols (HLS & DASH)](#10-streaming-protocols-hls--dash)

---

## 1. Audio Playback

### iOS - AVAudioPlayer

```swift
import AVFoundation

class AudioPlayerViewController: UIViewController {
    var audioPlayer: AVAudioPlayer?

    func playLocalAudio() {
        guard let audioURL = Bundle.main.url(forResource: "song", withExtension: "mp3") else {
            print("Audio file not found")
            return
        }

        do {
            audioPlayer = try AVAudioPlayer(contentsOf: audioURL)
            audioPlayer?.delegate = self
            audioPlayer?.play()
        } catch {
            print("Error initializing audio player: \(error)")
        }
    }

    func playRemoteAudio(urlString: String) {
        guard let url = URL(string: urlString) else { return }
        URLSession.shared.dataTask(with: url) { [weak self] data, _, error in
            guard let data = data, error == nil else { return }
            do {
                self?.audioPlayer = try AVAudioPlayer(data: data, fileTypeHint: .mp3)
                self?.audioPlayer?.play()
            } catch {
                print("Error: \(error)")
            }
        }.resume()
    }

    func setupNowPlayingControls() {
        var nowPlayingInfo = MPNowPlayingInfoCenter.default().nowPlayingInfo ?? [String: Any]()
        nowPlayingInfo[MPMediaItemPropertyTitle] = "Song Title"
        nowPlayingInfo[MPMediaItemPropertyArtist] = "Artist Name"
        nowPlayingInfo[MPMediaItemPropertyPlaybackDuration] = audioPlayer?.duration ?? 0
        nowPlayingInfo[MPNowPlayingInfoPropertyElapsedPlaybackTime] = audioPlayer?.currentTime ?? 0
        nowPlayingInfo[MPNowPlayingInfoPropertyPlaybackRate] = 1.0

        MPNowPlayingInfoCenter.default().nowPlayingInfo = nowPlayingInfo

        setupRemoteTransportControls()
    }

    func setupRemoteTransportControls() {
        let commandCenter = MPRemoteCommandCenter.shared()

        commandCenter.playCommand.addTarget { [weak self] _ in
            self?.audioPlayer?.play()
            return .success
        }

        commandCenter.pauseCommand.addTarget { [weak self] _ in
            self?.audioPlayer?.pause()
            return .success
        }

        commandCenter.skipForwardCommand.preferredIntervals = [15]
        commandCenter.skipForwardCommand.addTarget { [weak self] _ in
            let newTime = (self?.audioPlayer?.currentTime ?? 0) + 15
            self?.audioPlayer?.currentTime = newTime
            return .success
        }
    }

    func enableBackgroundAudio() {
        do {
            try AVAudioSession.sharedInstance().setCategory(
                .playback,
                mode: .default,
                options: [.duckOthers, .defaultToSpeaker]
            )
            try AVAudioSession.sharedInstance().setActive(true, options: .notifyOthersOnDeactivation)
        } catch {
            print("Audio session error: \(error)")
        }
    }
}

extension AudioPlayerViewController: AVAudioPlayerDelegate {
    func audioPlayerDidFinishPlaying(_ player: AVAudioPlayer, successfully flag: Bool) {
        if flag {
            print("Audio playback completed successfully")
        }
    }

    func audioPlayerDecodeErrorDidOccur(_ player: AVAudioPlayer, error: Error?) {
        print("Decode error: \(error?.localizedDescription ?? "Unknown error")")
    }
}
```

### Android - ExoPlayer

```kotlin
import androidx.media3.exoplayer.ExoPlayer
import androidx.media3.exoplayer.mediacontroller.MediaController
import androidx.media3.common.MediaItem
import androidx.media3.session.MediaSession
import androidx.media3.session.MediaSessionService

class AudioPlayerService : MediaSessionService() {
    private var mediaSession: MediaSession? = null

    override fun onCreate() {
        super.onCreate()
        initializeMediaSession()
    }

    private fun initializeMediaSession() {
        val player = ExoPlayer.Builder(this).build()
        mediaSession = MediaSession.Builder(this, player).build()
    }

    override fun onGetSession(controllerInfo: MediaSession.ControllerInfo): MediaSession? {
        return mediaSession
    }

    override fun onDestroy() {
        mediaSession?.run {
            player.release()
            release()
        }
        mediaSession = null
        super.onDestroy()
    }
}

class AudioPlayerActivity : AppCompatActivity() {
    private lateinit var player: ExoPlayer

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        player = ExoPlayer.Builder(this).build()

        // Play local audio
        val mediaItem = MediaItem.fromUri(Uri.parse("android.resource://${packageName}/${R.raw.song}"))
        player.setMediaItem(mediaItem)
        player.prepare()
        player.play()
    }

    fun playRemoteAudio(url: String) {
        val mediaItem = MediaItem.Builder()
            .setUri(url)
            .setMimeType("audio/mpeg")
            .build()

        player.setMediaItem(mediaItem)
        player.prepare()
        player.play()
    }

    fun setupNowPlayingControls() {
        val mediaMetadata = MediaMetadata.Builder()
            .setTitle("Song Title")
            .setArtist("Artist Name")
            .setArtworkUri(Uri.parse("artwork_url"))
            .build()

        player.mediaMetadata = mediaMetadata
    }

    override fun onDestroy() {
        player.release()
        super.onDestroy()
    }
}
```

---

## 2. Video Playback

### iOS - AVPlayer with PiP Support

```swift
import AVKit

class VideoPlayerViewController: UIViewController {
    private let playerViewController = AVPlayerViewController()
    private var player: AVPlayer?

    func setupVideoPlayback() {
        guard let videoURL = URL(string: "https://example.com/video.mp4") else { return }

        player = AVPlayer(url: videoURL)
        playerViewController.player = player

        addChild(playerViewController)
        view.addSubview(playerViewController.view)
        playerViewController.view.frame = view.bounds
        playerViewController.didMove(toParent: self)

        // Enable PiP
        playerViewController.allowsPictureInPicturePlayback = true
    }

    func playHLSStream(hlsURL: String) {
        guard let url = URL(string: hlsURL) else { return }

        let asset = AVAsset(url: url)
        let playerItem = AVPlayerItem(asset: asset)

        player = AVPlayer(playerItem: playerItem)
        playerViewController.player = player
        player?.play()
    }

    func setupPiPDelegate() {
        playerViewController.delegate = self
    }
}

extension VideoPlayerViewController: AVPlayerViewControllerDelegate {
    func playerViewControllerWillStartPictureInPicture(_ playerViewController: AVPlayerViewController) {
        print("PiP will start")
    }

    func playerViewControllerDidStopPictureInPicture(_ playerViewController: AVPlayerViewController) {
        print("PiP did stop")
    }
}
```

### Android - ExoPlayer with HLS/DASH

```kotlin
import androidx.media3.exoplayer.ExoPlayer
import androidx.media3.ui.PlayerView
import androidx.media3.common.MediaItem
import androidx.media3.common.MimeTypes

class VideoPlayerActivity : AppCompatActivity() {
    private lateinit var player: ExoPlayer
    private lateinit var playerView: PlayerView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        playerView = PlayerView(this)
        setContentView(playerView)

        player = ExoPlayer.Builder(this).build()
        playerView.player = player
    }

    fun playHLSStream(hlsUrl: String) {
        val mediaItem = MediaItem.Builder()
            .setUri(hlsUrl)
            .setMimeType(MimeTypes.APPLICATION_M3U8)
            .build()

        player.setMediaItem(mediaItem)
        player.prepare()
        player.play()
    }

    fun playDASHStream(dashUrl: String) {
        val mediaItem = MediaItem.Builder()
            .setUri(dashUrl)
            .setMimeType(MimeTypes.APPLICATION_MPD)
            .build()

        player.setMediaItem(mediaItem)
        player.prepare()
        player.play()
    }

    fun enablePiP() {
        val pipParams = PictureInPictureParams.Builder()
            .setAspectRatio(Rational(16, 9))
            .build()

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            enterPictureInPictureMode(pipParams)
        }
    }

    override fun onDestroy() {
        player.release()
        super.onDestroy()
    }
}
```

---

## 3. Camera Capture & Recording

### iOS - Photo & Video Capture

```swift
import AVFoundation
import Photos

class CameraViewController: UIViewController, AVCapturePhotoCaptureDelegate, AVCaptureFileOutputRecordingDelegate {
    private let captureSession = AVCaptureSession()
    private let photoOutput = AVCapturePhotoOutput()
    private let videoOutput = AVCaptureMovieFileOutput()
    private var previewLayer: AVCaptureVideoPreviewLayer?

    override func viewDidLoad() {
        super.viewDidLoad()
        setupCamera()
    }

    private func setupCamera() {
        guard let camera = AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: .front) else {
            print("No camera available")
            return
        }

        do {
            let input = try AVCaptureDeviceInput(device: camera)
            captureSession.addInput(input)
            captureSession.addOutput(photoOutput)
            captureSession.addOutput(videoOutput)

            previewLayer = AVCaptureVideoPreviewLayer(session: captureSession)
            previewLayer?.frame = view.bounds
            view.layer.addSublayer(previewLayer!)

            captureSession.startRunning()
        } catch {
            print("Error setting up camera: \(error)")
        }
    }

    func capturePhoto() {
        let settings = AVCapturePhotoSettings()
        settings.flashMode = .auto
        photoOutput.capturePhoto(with: settings, delegate: self)
    }

    func photoOutput(_ output: AVCapturePhotoOutput, didFinishProcessingPhoto photo: AVCapturePhoto, error: Error?) {
        guard let imageData = photo.fileDataRepresentation() else { return }

        PHPhotoLibrary.requestAuthorization { status in
            if status == .authorized {
                PHPhotoLibrary.shared().performChanges {
                    PHAssetChangeRequest.creationRequestForAsset(from: UIImage(data: imageData)!)
                }
            }
        }
    }

    func startVideoRecording() {
        let outputPath = NSTemporaryDirectory() + "video.mov"
        let outputURL = URL(fileURLWithPath: outputPath)
        videoOutput.startRecording(to: outputURL, recordingDelegate: self)
    }

    func stopVideoRecording() {
        videoOutput.stopRecording()
    }

    func fileOutput(_ output: AVCaptureFileOutput, didFinishRecordingTo outputFileURL: URL, from connections: [AVCaptureConnection], error: Error?) {
        if error == nil {
            PHPhotoLibrary.shared().performChanges {
                PHAssetChangeRequest.creationRequestForAssetFromVideo(atFileURL: outputFileURL)
            }
        }
    }
}
```

### Android - Camera & Recording

```kotlin
import android.Manifest
import android.content.pm.PackageManager
import androidx.camera.core.*
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.video.*
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat

class CameraActivity : AppCompatActivity() {
    private lateinit var cameraProvider: ProcessCameraProvider
    private var imageCapture: ImageCapture? = null
    private var videoCapture: VideoCapture<Recorder>? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        if (allPermissionsGranted()) {
            startCamera()
        } else {
            ActivityCompat.requestPermissions(
                this,
                arrayOf(Manifest.permission.CAMERA, Manifest.permission.RECORD_AUDIO),
                PERMISSION_REQUEST_CODE
            )
        }
    }

    private fun startCamera() {
        val cameraProviderFuture = ProcessCameraProvider.getInstance(this)

        cameraProviderFuture.addListener({
            cameraProvider = cameraProviderFuture.result

            val preview = Preview.Builder().build()
            val cameraSelector = CameraSelector.DEFAULT_FRONT_FACING

            imageCapture = ImageCapture.Builder().build()

            val recorder = Recorder.Builder().build()
            videoCapture = VideoCapture.withOutput(recorder)

            try {
                cameraProvider.unbindAll()
                cameraProvider.bindToLifecycle(
                    this, cameraSelector, preview, imageCapture, videoCapture
                )
                preview.setSurfaceProvider(binding.viewFinder.surfaceProvider)
            } catch (e: Exception) {
                Log.e(TAG, "Camera binding failed", e)
            }
        }, ContextCompat.getMainExecutor(this))
    }

    fun capturePhoto() {
        val imageCapture = imageCapture ?: return

        val outputOptions = ImageCapture.OutputFileOptions.Builder(
            File(filesDir, "photo.jpg")
        ).build()

        imageCapture.takePicture(
            outputOptions,
            ContextCompat.getMainExecutor(this),
            object : ImageCapture.OnImageSavedCallback {
                override fun onImageSaved(output: ImageCapture.OutputFileResults) {
                    Log.d(TAG, "Photo saved: ${output.savedUri}")
                }

                override fun onError(exception: ImageCaptureException) {
                    Log.e(TAG, "Photo capture failed", exception)
                }
            }
        )
    }

    fun startVideoRecording() {
        val videoCapture = videoCapture ?: return

        val outputOptions = FileOutputOptions.Builder(
            File(filesDir, "video.mp4")
        ).build()

        val recording = videoCapture.output
            .prepareRecording(this, outputOptions)
            .withAudioEnabled()
            .start(ContextCompat.getMainExecutor(this)) { recordingEvent ->
                when (recordingEvent) {
                    is VideoRecordEvent.Finalize -> {
                        Log.d(TAG, "Recording saved: ${recordingEvent.outputResults.outputUri}")
                    }
                    is VideoRecordEvent.Status -> {
                        Log.d(TAG, "Recording duration: ${recordingEvent.recordingStats.recordedDurationNanos}")
                    }
                }
            }
    }

    private fun allPermissionsGranted() = arrayOf(
        Manifest.permission.CAMERA,
        Manifest.permission.RECORD_AUDIO
    ).all {
        ContextCompat.checkSelfPermission(baseContext, it) == PackageManager.PERMISSION_GRANTED
    }
}
```

---

## 4. Social Sharing

### iOS - UIActivityViewController

```swift
class ShareViewController: UIViewController {
    func shareText(text: String) {
        let activityViewController = UIActivityViewController(
            activityItems: [text],
            applicationActivities: nil
        )

        activityViewController.completionWithItemsHandler = { activity, success, items, error in
            if success {
                print("Shared via: \(activity?.rawValue ?? "Unknown")")
            }
        }

        present(activityViewController, animated: true)
    }

    func shareImage(_ image: UIImage) {
        let activityViewController = UIActivityViewController(
            activityItems: [image],
            applicationActivities: nil
        )
        present(activityViewController, animated: true)
    }

    func shareURL(url: URL, withTitle title: String) {
        let activityViewController = UIActivityViewController(
            activityItems: [title, url],
            applicationActivities: nil
        )

        activityViewController.excludedActivityTypes = [.print, .saveToCameraRoll]

        present(activityViewController, animated: true)
    }

    func shareMultipleItems(image: UIImage, text: String, url: URL) {
        let activityViewController = UIActivityViewController(
            activityItems: [image, text, url],
            applicationActivities: nil
        )

        if let popoverController = activityViewController.popoverPresentationController {
            popoverController.sourceView = view
            popoverController.sourceRect = CGRect(x: view.bounds.midX, y: view.bounds.midY, width: 0, height: 0)
        }

        present(activityViewController, animated: true)
    }

    func setupShareExtension() {
        let shareURL = FileManager.default.containerURL(forSecurityApplicationGroupIdentifier: "group.com.app.shared")
        print("Share extension container: \(shareURL?.path ?? "Not found")")
    }
}
```

### Android - Share Intents

```kotlin
class ShareActivity : AppCompatActivity() {

    fun shareText(text: String) {
        val shareIntent = Intent().apply {
            action = Intent.ACTION_SEND
            putExtra(Intent.EXTRA_TEXT, text)
            type = "text/plain"
        }

        startActivity(Intent.createChooser(shareIntent, "Share via"))
    }

    fun shareImage(uri: Uri) {
        val shareIntent = Intent().apply {
            action = Intent.ACTION_SEND
            putExtra(Intent.EXTRA_STREAM, uri)
            type = "image/*"
        }

        startActivity(Intent.createChooser(shareIntent, "Share image"))
    }

    fun shareLink(url: String, title: String) {
        val shareIntent = Intent().apply {
            action = Intent.ACTION_SEND
            putExtra(Intent.EXTRA_TEXT, "$title\n$url")
            putExtra(Intent.EXTRA_SUBJECT, title)
            type = "text/plain"
        }

        startActivity(Intent.createChooser(shareIntent, "Share link"))
    }

    fun shareMultipleImages(uris: List<Uri>) {
        val shareIntent = Intent().apply {
            action = Intent.ACTION_SEND_MULTIPLE
            putParcelableArrayListExtra(Intent.EXTRA_STREAM, ArrayList(uris))
            type = "image/*"
        }

        startActivity(Intent.createChooser(shareIntent, "Share images"))
    }
}
```

---

## 5. In-App Chat - Stream SDK & Firebase

### Stream Chat Integration

```swift
// iOS - Stream Chat
import StreamChat
import StreamChatUI

class ChatViewController: UIViewController {
    let chatClient = ChatClient(config: .init(apiKey: "YOUR_API_KEY"))

    override func viewDidLoad() {
        super.viewDidLoad()
        setupStreamChat()
    }

    func setupStreamChat() {
        chatClient.connectUser(
            userInfo: UserInfo(id: "user123", name: "John Doe"),
            token: "YOUR_TOKEN"
        ) { result in
            switch result {
            case .success:
                print("Connected to Stream Chat")
                self.loadChannels()
            case .failure(let error):
                print("Connection failed: \(error)")
            }
        }
    }

    func loadChannels() {
        chatClient.channelListController(
            query: ChannelListQuery(filter: .containMembers(["user123"]))
        ) { result in
            switch result {
            case .success(let controller):
                print("Channels loaded: \(controller.channels.count)")
            case .failure(let error):
                print("Error loading channels: \(error)")
            }
        }
    }

    func sendMessage(channelId: String, text: String) {
        let channelController = chatClient.channelController(for: ChannelId(type: .messaging, id: channelId))
        channelController.createNewMessage(text: text) { result in
            switch result {
            case .success(let message):
                print("Message sent: \(message.text)")
            case .failure(let error):
                print("Error sending message: \(error)")
            }
        }
    }
}
```

### Firebase Realtime Database Chat

```kotlin
// Android - Firebase Chat
import com.google.firebase.database.*
import com.google.firebase.auth.FirebaseAuth

data class Message(
    val userId: String = "",
    val userName: String = "",
    val text: String = "",
    val timestamp: Long = 0
)

class ChatActivity : AppCompatActivity() {
    private val database = FirebaseDatabase.getInstance()
    private val auth = FirebaseAuth.getInstance()
    private val messagesRef = database.getReference("messages")

    fun sendMessage(chatId: String, text: String) {
        val currentUser = auth.currentUser ?: return

        val message = Message(
            userId = currentUser.uid,
            userName = currentUser.displayName ?: "Anonymous",
            text = text,
            timestamp = System.currentTimeMillis()
        )

        messagesRef.child(chatId).push().setValue(message)
            .addOnSuccessListener {
                Log.d(TAG, "Message sent")
            }
            .addOnFailureListener { e ->
                Log.e(TAG, "Send failed", e)
            }
    }

    fun listenForMessages(chatId: String) {
        messagesRef.child(chatId).addValueEventListener(object : ValueEventListener {
            override fun onDataChange(snapshot: DataSnapshot) {
                val messages = mutableListOf<Message>()
                snapshot.children.forEach { child ->
                    val message = child.getValue(Message::class.java)
                    message?.let { messages.add(it) }
                }
                updateUI(messages)
            }

            override fun onCancelled(error: DatabaseError) {
                Log.e(TAG, "Database error", error.toException())
            }
        })
    }

    private fun updateUI(messages: List<Message>) {
        // Update RecyclerView with messages
    }
}
```

---

## 6. Real-time Features - Presence & Typing Indicators

### Presence Indicators

```swift
// iOS - Stream Chat Presence
class ChatController {
    func updatePresence(userId: String, isOnline: Bool) {
        chatClient.userController.updateUserPresence(isOnline: isOnline) { result in
            switch result {
            case .success:
                print("Presence updated: \(isOnline ? "online" : "offline")")
            case .failure(let error):
                print("Presence update failed: \(error)")
            }
        }
    }

    func monitorUserPresence(userId: String) {
        chatClient.currentUserController?.observeCurrentUser { [weak self] user in
            print("Current user: \(user.presence)")
        }
    }
}
```

```kotlin
// Android - Firebase Presence
class PresenceManager(userId: String) {
    private val userStatusDatabase = FirebaseDatabase.getInstance().getReference("status/$userId")
    private val connectedRef = FirebaseDatabase.getInstance().getReference(".info/connected")

    fun setupPresence() {
        connectedRef.addValueEventListener(object : ValueEventListener {
            override fun onDataChange(snapshot: DataSnapshot) {
                val connected = snapshot.getValue(Boolean::class.java) ?: false

                if (connected) {
                    userStatusDatabase.onDisconnect().setValue(mapOf("state" to "offline"))
                    userStatusDatabase.setValue(mapOf("state" to "online"))
                }
            }

            override fun onCancelled(error: DatabaseError) {
                Log.e(TAG, "Presence error", error.toException())
            }
        })
    }

    fun observeUserPresence(userId: String) {
        FirebaseDatabase.getInstance().getReference("status/$userId")
            .addValueEventListener(object : ValueEventListener {
                override fun onDataChange(snapshot: DataSnapshot) {
                    val userStatus = snapshot.getValue(String::class.java)
                    Log.d(TAG, "User $userId status: $userStatus")
                }

                override fun onCancelled(error: DatabaseError) {}
            })
    }
}
```

### Typing Indicators

```swift
// iOS - Typing Indicators
class TypingController {
    func sendTypingIndicator(channelId: String) {
        let channelController = chatClient.channelController(for: ChannelId(type: .messaging, id: channelId))
        channelController.sendTypingEvent { result in
            print("Typing indicator sent")
        }
    }

    func stopTypingIndicator(channelId: String) {
        let channelController = chatClient.channelController(for: ChannelId(type: .messaging, id: channelId))
        channelController.sendStopTypingEvent { result in
            print("Stop typing indicator sent")
        }
    }

    func observeTypingUsers(channelId: String) {
        let channelController = chatClient.channelController(for: ChannelId(type: .messaging, id: channelId))
        channelController.$typingUsers.sink { typingUsers in
            print("Currently typing: \(typingUsers.map { $0.name })")
        }.store(in: &cancellables)
    }
}
```

```kotlin
// Android - Typing Indicators
class TypingIndicatorManager {
    private val typingRef = FirebaseDatabase.getInstance().getReference("typing")

    fun sendTypingIndicator(channelId: String, userId: String) {
        typingRef.child(channelId).child(userId).setValue(true)

        // Auto-stop typing after 3 seconds of inactivity
        Handler(Looper.getMainLooper()).postDelayed({
            stopTypingIndicator(channelId, userId)
        }, 3000)
    }

    fun stopTypingIndicator(channelId: String, userId: String) {
        typingRef.child(channelId).child(userId).removeValue()
    }

    fun observeTypingUsers(channelId: String) {
        typingRef.child(channelId).addValueEventListener(object : ValueEventListener {
            override fun onDataChange(snapshot: DataSnapshot) {
                val typingUsers = mutableListOf<String>()
                snapshot.children.forEach { child ->
                    typingUsers.add(child.key ?: "")
                }
                updateTypingIndicator(typingUsers)
            }

            override fun onCancelled(error: DatabaseError) {}
        })
    }

    private fun updateTypingIndicator(typingUsers: List<String>) {
        val text = when {
            typingUsers.isEmpty() -> ""
            typingUsers.size == 1 -> "${typingUsers[0]} is typing..."
            else -> "${typingUsers.joinToString(", ")} are typing..."
        }
        // Update UI
    }
}
```

---

## 7. User-Generated Content & Moderation

```swift
// iOS - Content Moderation
import Vision

class ContentModerationManager {
    func moderateText(_ text: String, completion: @escaping (Bool) -> Void) {
        let bannedWords = ["badword1", "badword2", "offensive"]

        let lowercaseText = text.lowercased()
        let isClean = !bannedWords.contains { lowercaseText.contains($0) }

        completion(isClean)
    }

    func reportContent(contentId: String, reason: String, userId: String) {
        let report = [
            "contentId": contentId,
            "reason": reason,
            "reportedBy": userId,
            "timestamp": Date().timeIntervalSince1970
        ]

        // Send to backend for review
        let reportRef = FirebaseDatabase.database().reference().child("reports").childByAutoId()
        reportRef.setValue(report)
    }

    func detectImageContent(image: UIImage, completion: @escaping ([VNClassificationObservation]) -> Void) {
        guard let ciImage = CIImage(image: image) else { return }

        let request = VNCoreMLRequest(model: try! VNCoreMLModel(for: MobileNetV2().model)) { request, error in
            guard let results = request.results as? [VNClassificationObservation] else { return }
            completion(results)
        }

        let handler = VNImageRequestHandler(ciImage: ciImage)
        try? handler.perform([request])
    }
}
```

```kotlin
// Android - Content Moderation
class ContentModerationManager {
    private val bannedWords = setOf("badword1", "badword2", "offensive")
    private val database = FirebaseDatabase.getInstance()

    fun moderateText(text: String): Boolean {
        val lowercaseText = text.lowercase()
        return !bannedWords.any { lowercaseText.contains(it) }
    }

    fun reportContent(contentId: String, reason: String, userId: String) {
        val report = mapOf(
            "contentId" to contentId,
            "reason" to reason,
            "reportedBy" to userId,
            "timestamp" to System.currentTimeMillis()
        )

        database.getReference("reports").push().setValue(report)
            .addOnSuccessListener {
                Log.d(TAG, "Report submitted")
            }
            .addOnFailureListener { e ->
                Log.e(TAG, "Report failed", e)
            }
    }

    fun flagUserForReview(userId: String, reason: String) {
        val flag = mapOf(
            "userId" to userId,
            "reason" to reason,
            "flaggedAt" to System.currentTimeMillis()
        )

        database.getReference("flagged_users").child(userId).setValue(flag)
    }
}
```

---

## 8. Image & Video Compression

### iOS Compression

```swift
class MediaCompressionManager {
    func compressImage(_ image: UIImage, quality: CGFloat = 0.5) -> Data? {
        return image.jpegData(compressionQuality: quality)
    }

    func compressVideo(inputURL: URL, outputURL: URL, completion: @escaping (Bool) -> Void) {
        let asset = AVAsset(url: inputURL)

        guard let exportSession = AVAssetExportSession(
            asset: asset,
            presetName: AVAssetExportPresetMediumQuality
        ) else {
            completion(false)
            return
        }

        exportSession.outputURL = outputURL
        exportSession.outputFileType = .mp4

        exportSession.exportAsynchronously {
            completion(exportSession.status == .completed)
        }
    }

    func getThumbnail(videoURL: URL) -> UIImage? {
        let asset = AVAsset(url: videoURL)
        let generator = AVAssetImageGenerator(asset: asset)

        do {
            let cgImage = try generator.copyCGImage(at: CMTime(seconds: 0, preferredTimescale: 600), actualTime: nil)
            return UIImage(cgImage: cgImage)
        } catch {
            return nil
        }
    }
}
```

### Android Compression

```kotlin
class MediaCompressionManager {

    fun compressImage(bitmap: Bitmap, quality: Int = 50): ByteArray {
        val outputStream = ByteArrayOutputStream()
        bitmap.compress(Bitmap.CompressFormat.JPEG, quality, outputStream)
        return outputStream.toByteArray()
    }

    fun compressVideo(inputPath: String, outputPath: String) {
        val mediaMetadataRetriever = MediaMetadataRetriever()
        mediaMetadataRetriever.setDataSource(inputPath)

        val videoWidth = mediaMetadataRetriever
            .extractMetadata(MediaMetadataRetriever.METADATA_KEY_VIDEO_WIDTH)?.toInt() ?: 1920
        val videoHeight = mediaMetadataRetriever
            .extractMetadata(MediaMetadataRetriever.METADATA_KEY_VIDEO_HEIGHT)?.toInt() ?: 1080

        // Use MediaMuxer for compression
        val outputFormat = MediaMuxer(outputPath, MediaMuxer.OutputFormat.MUXER_OUTPUT_MPEG_4)

        // Configure encoder and decode/encode video
    }

    fun getVideoThumbnail(videoPath: String): Bitmap? {
        return ThumbnailUtils.createVideoThumbnail(
            videoPath,
            MediaStore.Images.Thumbnails.MINI_KIND
        )
    }
}
```

---

## 9. Media Caching Strategies

```swift
// iOS - Image Caching with SDWebImage pattern
class MediaCacheManager {
    static let shared = MediaCacheManager()

    private let memoryCache = NSCache<NSString, UIImage>()
    private let diskCache = FileManager.default.urls(for: .cachesDirectory, in: .userDomainMask)[0]

    func cacheImage(_ image: UIImage, for key: String) {
        memoryCache.setObject(image, forKey: key as NSString)
        saveToDisk(image: image, for: key)
    }

    func cachedImage(for key: String) -> UIImage? {
        if let cached = memoryCache.object(forKey: key as NSString) {
            return cached
        }

        if let diskImage = loadFromDisk(for: key) {
            memoryCache.setObject(diskImage, forKey: key as NSString)
            return diskImage
        }

        return nil
    }

    private func saveToDisk(image: UIImage, for key: String) {
        guard let data = image.jpegData(compressionQuality: 0.8) else { return }
        let fileURL = diskCache.appendingPathComponent(key)
        try? data.write(to: fileURL)
    }

    private func loadFromDisk(for key: String) -> UIImage? {
        let fileURL = diskCache.appendingPathComponent(key)
        guard let data = try? Data(contentsOf: fileURL) else { return nil }
        return UIImage(data: data)
    }

    func clearCache() {
        memoryCache.removeAllObjects()
        try? FileManager.default.removeItem(at: diskCache)
    }
}
```

```kotlin
// Android - Media Caching with Glide pattern
class MediaCacheManager(context: Context) {
    private val context = context
    private val memoryCache = LruCache<String, Bitmap>(maxSize = 10)

    fun cacheImage(bitmap: Bitmap, key: String) {
        memoryCache.put(key, bitmap)
        saveToDisk(bitmap, key)
    }

    fun getCachedImage(key: String): Bitmap? {
        memoryCache.get(key)?.let { return it }

        val cached = loadFromDisk(key)
        cached?.let { memoryCache.put(key, it) }
        return cached
    }

    private fun saveToDisk(bitmap: Bitmap, key: String) {
        val file = File(context.cacheDir, key)
        file.outputStream().use { outputStream ->
            bitmap.compress(Bitmap.CompressFormat.JPEG, 80, outputStream)
        }
    }

    private fun loadFromDisk(key: String): Bitmap? {
        val file = File(context.cacheDir, key)
        return if (file.exists()) {
            BitmapFactory.decodeFile(file.absolutePath)
        } else {
            null
        }
    }

    fun clearCache() {
        memoryCache.evictAll()
        context.cacheDir.deleteRecursively()
    }
}
```

---

## 10. Streaming Protocols (HLS & DASH)

### HLS (HTTP Live Streaming)

```swift
// iOS - HLS Stream Implementation
class HLSStreamingManager {
    func setupHLSPlayback(playlistURL: String) {
        guard let url = URL(string: playlistURL) else { return }

        let asset = AVAsset(url: url)

        // Monitor loading of AVAsset
        asset.loadValuesAsynchronously(forKeys: ["playable"]) {
            DispatchQueue.main.async {
                let playerItem = AVPlayerItem(asset: asset)
                let player = AVPlayer(playerItem: playerItem)
                player.play()
            }
        }
    }

    func configureABR(player: AVPlayer) {
        if let playerItem = player.currentItem {
            // Configure bit rate preferences
            playerItem.preferredPeakBitRate = 5_000_000 // 5 Mbps
            playerItem.preferredMaximumResolution = CGSize(width: 1920, height: 1080)
        }
    }

    func handleStreamError(_ error: Error) {
        print("HLS Error: \(error.localizedDescription)")
        // Implement retry logic with exponential backoff
    }
}
```

### DASH (Dynamic Adaptive Streaming over HTTP)

```kotlin
// Android - DASH Stream Implementation
class DASHStreamingManager {

    fun setupDASHPlayback(mpdUrl: String, player: ExoPlayer) {
        val mediaSource = DashMediaSource.Factory(
            DefaultHttpDataSource.Factory()
        ).createMediaSource(MediaItem.fromUri(mpdUrl))

        player.setMediaSource(mediaSource)
        player.prepare()
        player.play()
    }

    fun configureAdaptiveBitrate(player: ExoPlayer) {
        val trackSelector = DefaultTrackSelector(context)
        trackSelector.setParameters(
            DefaultTrackSelector.ParametersBuilder(context)
                .setMaxVideoSize(1920, 1080)
                .setMaxVideoBitrate(5000000) // 5 Mbps
                .build()
        )
    }

    fun monitorStreamQuality(player: ExoPlayer) {
        player.addAnalyticsListener(object : AnalyticsListener {
            override fun onVideoInputFormatChanged(
                eventTime: AnalyticsListener.EventTime,
                format: Format
            ) {
                Log.d(TAG, "Video quality changed: ${format.bitrate} bps")
            }
        })
    }
}
```

---

## Performance Tips

1. **Audio**: Always use appropriate audio session categories for your use case
2. **Video**: Enable hardware acceleration when available
3. **Camera**: Request permissions early and handle gracefully
4. **Sharing**: Provide appropriate fallback options for share extensions
5. **Chat**: Implement pagination for message history
6. **Presence**: Debounce presence updates to reduce database writes
7. **Compression**: Balance quality and file size based on network conditions
8. **Caching**: Implement TTL-based cache invalidation
9. **Streaming**: Use adaptive bitrate algorithms for better user experience
10. **Moderation**: Combine client-side and server-side moderation for security

---

## Security Considerations

- Use HTTPS for all remote media URLs
- Validate user-generated content before storage
- Implement rate limiting on chat/messaging endpoints
- Store sensitive tokens securely (Keychain on iOS, Keystore on Android)
- Encrypt media data at rest
- Implement proper access controls for user content
- Sanitize user input to prevent injection attacks
- Use secure WebSocket connections for real-time features
