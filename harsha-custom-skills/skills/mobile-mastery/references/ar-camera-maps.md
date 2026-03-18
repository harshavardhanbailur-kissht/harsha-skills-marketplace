# AR/Camera/Maps Reference Guide

## Table of Contents
- [1. ARKit (iOS)](#1-arkit-ios)
- [2. ARCore (Android)](#2-arcore-android)
- [3. Camera APIs](#3-camera-apis)
- [4. Image Processing](#4-image-processing)
- [5. QR/Barcode Scanning](#5-qrbarcode-scanning)
- [6. Maps](#6-maps)
- [7. Geolocation](#7-geolocation)
- [8. Geocoding & Reverse Geocoding](#8-geocoding--reverse-geocoding)
- [9. Geofencing & Location Permissions](#9-geofencing--location-permissions)
- [10. Background Location Tracking](#10-background-location-tracking)
- [11. Custom Map Annotations & Overlays](#11-custom-map-annotations--overlays)
- [12. Indoor Positioning Basics](#12-indoor-positioning-basics)

## 1. ARKit (iOS)

### Plane Detection
```swift
import ARKit

class PlaneDetectionViewController: UIViewController, ARSessionDelegate {
    let arView = ARView(frame: .zero)
    var arSession = ARSession()

    override func viewDidLoad() {
        super.viewDidLoad()
        view.addSubview(arView)
        arView.session = arSession

        let configuration = ARWorldTrackingConfiguration()
        configuration.planeDetection = [.horizontal, .vertical]
        configuration.environmentTexturing = .automatic

        if ARWorldTrackingConfiguration.supportsFrameSemantics(.personSegmentationWithDepth) {
            configuration.frameSemantics.insert(.personSegmentationWithDepth)
        }

        arSession.run(configuration)
    }
}
```

### World Tracking & RealityKit
```swift
import RealityKit

class WorldTrackingView: UIView {
    @State var modelContainer: ModelContainer?

    func setupAnchor() {
        var anchor = ModelAnchor(name: "model", model: try? ModelEntity.loadModel(named: "robot"))
        anchor.transform.translation.y = 0.5

        try? arView.scene.addAnchor(anchor)
    }

    func detectPlanes(_ frame: ARFrame) {
        if let detection = frame.anchors.compactMap({ $0 as? PlaneAnchor }) {
            for plane in detection {
                print("Detected plane: \(plane.extent)")
            }
        }
    }
}
```

### Face Tracking
```swift
class FaceTrackingController: UIViewController {
    func setupFaceTracking() {
        guard ARFaceTrackingConfiguration.isSupported else { return }

        let configuration = ARFaceTrackingConfiguration()
        configuration.maximumNumberOfTrackedFaces = ARFaceTrackingConfiguration.supportedNumberOfTrackedFaces
        configuration.isLightEstimationEnabled = true

        arSession.run(configuration)
    }

    func captureBlendShapes(_ faceAnchor: ARFaceAnchor) {
        let blendShapes = faceAnchor.blendShapes

        if let jawOpen = blendShapes[.jawOpen]?.floatValue {
            print("Jaw open: \(jawOpen)")
        }

        if let mouthSmile = blendShapes[.mouthSmileLeft]?.floatValue {
            print("Smile intensity: \(mouthSmile)")
        }

        // Available shapes: eyeBlinkLeft/Right, eyeWideLeft/Right, jawForward, etc.
    }
}
```

---

## 2. ARCore (Android)

### Motion Tracking
```kotlin
import com.google.ar.core.*

class MotionTrackingActivity : AppCompatActivity() {
    private lateinit var session: Session
    private lateinit var arSceneView: ArSceneView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_ar)

        arSceneView = findViewById(R.id.arSceneView)
        session = Session(this)

        val config = Config(session)
        config.updateMode = Config.UpdateMode.LATEST_CAMERA_IMAGE
        session.configure(config)
    }

    fun processMotion(frame: Frame) {
        val pose = frame.camera.pose
        val translation = pose.translation // [x, y, z]
        val rotation = pose.rotationQuaternion // [qx, qy, qz, qw]

        println("Position: ${translation.contentToString()}")
    }
}
```

### Environmental Understanding
```kotlin
class EnvironmentalTracking {
    fun detectPlanes(session: Session, frame: Frame) {
        val planes = frame.getAllUpdatedTrackables(Plane::class.java)

        for (plane in planes) {
            if (plane.trackingState == TrackingState.TRACKING) {
                val extentX = plane.extentX
                val extentZ = plane.extentZ
                val centerPose = plane.centerPose

                println("Plane detected: ${plane.type} - " +
                    "Size: ${extentX}x${extentZ}")
            }
        }
    }

    fun detectLightEstimates(frame: Frame) {
        val lightEstimate = frame.lightEstimate
        val colorCorrection = lightEstimate.colorCorrection // FloatBuffer RGBA
        val pixelIntensity = lightEstimate.pixelIntensity

        println("Environment brightness: $pixelIntensity")
    }
}
```

### Light Estimation
```kotlin
class LightEstimationHandler {
    fun adjustLightingForModel(lightEstimate: com.google.ar.core.LightEstimate) {
        val intensity = lightEstimate.pixelIntensity
        val mainLight = lightEstimate.mainLight

        // mainLight direction (normalized): [x, y, z]
        val direction = mainLight.direction

        // Create proper lighting environment
        val ambientIntensity = intensity / 255f
        println("Ambient light intensity: $ambientIntensity")

        // Apply to 3D rendering (e.g., Sceneform or Filament)
    }
}
```

---

## 3. Camera APIs

### iOS: AVFoundation
```swift
import AVFoundation

class CameraController: NSObject, AVCapturePhotoCaptureDelegate {
    var captureSession = AVCaptureSession()
    var photoOutput = AVCapturePhotoOutput()

    func setupCamera() {
        captureSession.sessionPreset = .high

        guard let device = AVCaptureDevice.default(.builtInWideAngleCamera,
                                                     for: .video,
                                                     position: .front) else { return }

        do {
            let input = try AVCaptureDeviceInput(device: device)
            captureSession.addInput(input)
            captureSession.addOutput(photoOutput)
            captureSession.startRunning()
        } catch {
            print("Camera setup error: \(error)")
        }
    }

    func capturePhoto() {
        let settings = AVCapturePhotoSettings()
        settings.flashMode = .auto
        photoOutput.capturePhoto(with: settings, delegate: self)
    }

    func photoOutput(_ output: AVCapturePhotoOutput,
                     didFinishProcessingPhoto photo: AVCapturePhoto,
                     error: Error?) {
        guard let imageData = photo.fileDataRepresentation() else { return }
        let uiImage = UIImage(data: imageData)
        // Process image
    }
}
```

### Android: CameraX
```kotlin
import androidx.camera.core.*
import androidx.camera.lifecycle.ProcessCameraProvider
import java.util.concurrent.ExecutorService

class CameraXController(private val lifecycleOwner: LifecycleOwner,
                        private val previewView: PreviewView) {
    private lateinit var cameraExecutor: ExecutorService

    fun startCamera() {
        val cameraProviderFuture = ProcessCameraProvider.getInstance(context)

        cameraProviderFuture.addListener({
            val cameraProvider = cameraProviderFuture.result

            val preview = Preview.Builder().build().also {
                it.setSurfaceProvider(previewView.surfaceProvider)
            }

            val imageCapture = ImageCapture.Builder()
                .setTargetResolution(android.util.Size(1080, 1920))
                .setCaptureMode(ImageCapture.CAPTURE_MODE_MINIMIZE_LATENCY)
                .build()

            val cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA

            try {
                cameraProvider.unbindAll()
                cameraProvider.bindToLifecycle(
                    lifecycleOwner, cameraSelector, preview, imageCapture)
            } catch(exc: Exception) {
                Log.e("CameraX", "Use case binding failed", exc)
            }
        }, ContextCompat.getMainExecutor(context))
    }
}
```

### Video Capture (iOS)
```swift
func setupVideoCapture() {
    let videoOutput = AVCaptureVideoDataOutput()
    videoOutput.videoSettings = [
        kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA
    ]

    let queue = DispatchQueue(label: "com.camera.queue")
    videoOutput.setSampleBufferDelegate(self, queue: queue)

    captureSession.addOutput(videoOutput)
}

extension CameraController: AVCaptureVideoDataOutputSampleBufferDelegate {
    func captureOutput(_ output: AVCaptureOutput,
                       didOutput sampleBuffer: CMSampleBuffer,
                       from connection: AVCaptureConnection) {
        guard let imageBuffer = CMSampleBufferGetImageBuffer(sampleBuffer) else { return }
        // Real-time video frame processing
    }
}
```

---

## 4. Image Processing

### iOS: CIFilter
```swift
import CoreImage

class ImageProcessingController {
    let context = CIContext()

    func applyFilters(_ image: UIImage) -> UIImage? {
        guard let ciImage = CIImage(image: image) else { return nil }

        // Blur filter
        let blurFilter = CIFilter(name: "CIGaussianBlur")
        blurFilter?.setValue(ciImage, forKey: kCIInputImageKey)
        blurFilter?.setValue(15, forKey: kCIInputRadiusKey)

        // Color adjustment
        let colorFilter = CIFilter(name: "CIColorControls")
        colorFilter?.setValue(blurFilter?.outputImage, forKey: kCIInputImageKey)
        colorFilter?.setValue(1.5, forKey: kCIInputSaturationKey)

        // Edge detection
        let edgeFilter = CIFilter(name: "CIEdges")
        edgeFilter?.setValue(colorFilter?.outputImage, forKey: kCIInputImageKey)

        guard let outputImage = edgeFilter?.outputImage,
              let cgImage = context.createCGImage(outputImage,
                                                  from: outputImage.extent) else {
            return nil
        }

        return UIImage(cgImage: cgImage)
    }

    func applyCoreMLModel(_ image: UIImage) {
        // Integration with Vision + CoreML
        let visionRequest = VNCoreMLRequest(model: model) { request, error in
            if let results = request.results as? [VNClassificationObservation] {
                for observation in results {
                    print("\(observation.identifier): \(observation.confidence)")
                }
            }
        }
    }
}
```

### Android: Image Manipulation
```kotlin
import android.graphics.*

class ImageProcessing {
    fun applyGaussianBlur(bitmap: Bitmap, radius: Float): Bitmap {
        val renderScript = RenderScript.create(context)
        val input = Allocation.createFromBitmap(renderScript, bitmap)
        val output = Allocation.createTyped(renderScript, input.type)

        val blur = ScriptIntrinsicBlur.create(renderScript, Element.U8_4(renderScript))
        blur.setRadius(radius)
        blur.setInput(input)
        blur.forEach(output)

        output.copyTo(bitmap)
        renderScript.destroy()
        return bitmap
    }

    fun detectEdges(bitmap: Bitmap): Bitmap {
        val width = bitmap.width
        val height = bitmap.height
        val result = Bitmap.createBitmap(width, height, Bitmap.Config.RGB_565)

        val grayBitmap = toGrayscale(bitmap)
        val pixels = IntArray(width * height)
        grayBitmap.getPixels(pixels, 0, width, 0, 0, width, height)

        // Sobel edge detection
        for (y in 1 until height - 1) {
            for (x in 1 until width - 1) {
                val gx = calculateSobelX(pixels, x, y, width)
                val gy = calculateSobelY(pixels, x, y, width)
                val magnitude = sqrt((gx * gx + gy * gy).toFloat()).toInt()
                result.setPixel(x, y, Color.rgb(magnitude, magnitude, magnitude))
            }
        }
        return result
    }
}
```

---

## 5. QR/Barcode Scanning

### iOS: Vision Framework
```swift
import Vision

class QRScannerController: UIViewController {
    func setupVisionRequest() -> VNDetectBarcodesRequest {
        let request = VNDetectBarcodesRequest(completionHandler: barcodesDidComplete)
        request.symbologies = [.QR, .code128, .code39, .ean13]
        return request
    }

    private func barcodesDidComplete(request: VNRequest, error: Error?) {
        guard let results = request.results as? [VNBarcodeObservation] else { return }

        for barcode in results {
            if let payload = barcode.payloadStringValue {
                print("Scanned: \(payload)")
                handleScannedData(payload)
            }
        }
    }

    func performVisionRequest(_ cgImage: CGImage) {
        let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
        try? handler.perform([setupVisionRequest()])
    }
}
```

### Android: ML Kit Barcode
```kotlin
import com.google.mlkit.vision.barcode.BarcodeScannerOptions
import com.google.mlkit.vision.barcode.BarcodeScanning
import com.google.mlkit.vision.common.InputImage

class MLKitBarcodeScanner {
    fun scanBarcode(bitmap: Bitmap) {
        val options = BarcodeScannerOptions.Builder()
            .setBarcodeFormats(
                Barcode.FORMAT_QR_CODE,
                Barcode.FORMAT_CODE_128,
                Barcode.FORMAT_EAN_13
            )
            .build()

        val scanner = BarcodeScanning.getClient(options)
        val image = InputImage.fromBitmap(bitmap)

        scanner.process(image)
            .addOnSuccessListener { barcodes ->
                for (barcode in barcodes) {
                    val rawValue = barcode.rawValue
                    val format = barcode.format
                    println("Barcode: $rawValue (Format: $format)")
                }
            }
            .addOnFailureListener { e ->
                Log.e("BarcodeScanner", "Scanning failed", e)
            }
    }
}
```

---

## 6. Maps

### iOS: MapKit
```swift
import MapKit

class MapViewController: UIViewController {
    @IBOutlet weak var mapView: MKMapView!

    override func viewDidLoad() {
        super.viewDidLoad()

        let initialLocation = CLLocationCoordinate2D(latitude: 37.7749, longitude: -122.4194)
        let region = MKCoordinateRegion(
            center: initialLocation,
            span: MKCoordinateSpan(latitudeDelta: 0.05, longitudeDelta: 0.05)
        )
        mapView.setRegion(region, animated: true)

        // Add annotation
        let annotation = MKPointAnnotation()
        annotation.coordinate = initialLocation
        annotation.title = "San Francisco"
        annotation.subtitle = "Golden Gate City"
        mapView.addAnnotation(annotation)
    }

    func addCustomAnnotation() {
        let annotation = MKPointAnnotation()
        annotation.coordinate = CLLocationCoordinate2D(latitude: 37.8044, longitude: -122.2712)
        annotation.title = "Golden Gate Bridge"
        mapView.addAnnotation(annotation)
    }

    func drawPolyline(coordinates: [CLLocationCoordinate2D]) {
        let polyline = MKPolyline(coordinates: coordinates, count: coordinates.count)
        mapView.addOverlay(polyline)
    }
}

extension MapViewController: MKMapViewDelegate {
    func mapView(_ mapView: MKMapView, viewFor annotation: MKAnnotation) -> MKAnnotationView? {
        guard !(annotation is MKUserLocation) else { return nil }

        let annotationView = MKMarkerAnnotationView(annotation: annotation, reuseIdentifier: "marker")
        annotationView.markerTintColor = .systemBlue
        annotationView.canShowCallout = true
        return annotationView
    }

    func mapView(_ mapView: MKMapView, rendererFor overlay: MKOverlay) -> MKOverlayRenderer {
        guard let polyline = overlay as? MKPolyline else { return MKOverlayRenderer() }

        let renderer = MKPolylineRenderer(polyline: polyline)
        renderer.strokeColor = .systemBlue
        renderer.lineWidth = 3
        return renderer
    }
}
```

### Android: Google Maps SDK
```kotlin
import com.google.android.gms.maps.CameraUpdateFactory
import com.google.android.gms.maps.GoogleMap
import com.google.android.gms.maps.SupportMapFragment
import com.google.android.gms.maps.model.*

class MapActivity : AppCompatActivity() {
    private lateinit var googleMap: GoogleMap

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_map)

        val mapFragment = supportFragmentManager.findFragmentById(R.id.map) as SupportMapFragment
        mapFragment.getMapAsync { map ->
            googleMap = map
            setupMap()
        }
    }

    private fun setupMap() {
        val sydney = LatLng(-33.852, 151.211)
        googleMap.addMarker(MarkerOptions().position(sydney).title("Sydney"))
        googleMap.moveCamera(CameraUpdateFactory.newLatLngZoom(sydney, 12f))

        googleMap.setOnMarkerClickListener { marker ->
            println("Marker clicked: ${marker.title}")
            true
        }
    }

    fun drawPolyline() {
        val points = listOf(
            LatLng(-33.852, 151.211),
            LatLng(-33.857, 151.215),
            LatLng(-33.860, 151.220)
        )

        val polyline = googleMap.addPolyline(PolylineOptions()
            .addAll(points)
            .color(Color.BLUE)
            .width(5f)
            .geodesic(true))
    }

    fun addCircle() {
        googleMap.addCircle(CircleOptions()
            .center(LatLng(-33.852, 151.211))
            .radius(1000.0)
            .fillColor(Color.argb(50, 0, 0, 255))
            .strokeColor(Color.BLUE)
            .strokeWidth(2f))
    }
}
```

### Mapbox Integration
```swift
import Mapbox

class MapboxViewController: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()

        let mapView = MGLMapView(frame: view.bounds)
        mapView.styleURL = MGLStyle.outdoorsStyleURL
        mapView.zoomLevel = 12
        mapView.centerCoordinate = CLLocationCoordinate2D(latitude: 37.7749, longitude: -122.4194)
        view.addSubview(mapView)

        // Custom style layer
        if let style = mapView.style {
            let source = MGLShapeSource(identifier: "source", shape: nil, options: nil)
            style.addSource(source)

            let layer = MGLCircleStyleLayer(identifier: "layer", source: source)
            layer.circleRadius = NSExpression(forConstantValue: 10)
            layer.circleColor = NSExpression(forConstantValue: UIColor.blue)
            style.addLayer(layer)
        }
    }
}
```

### React Native Maps
```javascript
import MapView, { Marker, Polyline, Circle } from 'react-native-maps';

const MapComponent = () => {
  const initialRegion = {
    latitude: 37.7749,
    longitude: -122.4194,
    latitudeDelta: 0.0922,
    longitudeDelta: 0.0421,
  };

  return (
    <MapView
      style={{ flex: 1 }}
      initialRegion={initialRegion}
      onPress={(e) => console.log(e.nativeEvent.coordinate)}
    >
      <Marker
        coordinate={{ latitude: 37.7749, longitude: -122.4194 }}
        title="San Francisco"
        description="Golden Gate City"
      />

      <Polyline
        coordinates={[
          { latitude: 37.7749, longitude: -122.4194 },
          { latitude: 37.8044, longitude: -122.2712 },
        ]}
        strokeColor="#FF0000"
        strokeWidth={3}
      />

      <Circle
        center={{ latitude: 37.7749, longitude: -122.4194 }}
        radius={1000}
        fillColor="rgba(0,0,255,0.1)"
        strokeColor="rgba(0,0,255,1)"
      />
    </MapView>
  );
};
```

---

## 7. Geolocation

### iOS: Core Location
```swift
import CoreLocation

class LocationManager: NSObject, CLLocationManagerDelegate {
    let manager = CLLocationManager()
    var locationUpdates: ((CLLocation) -> Void)?

    override init() {
        super.init()
        manager.delegate = self
        manager.desiredAccuracy = kCLLocationAccuracyBest
        manager.distanceFilter = 10 // Update every 10 meters
    }

    func requestPermission() {
        manager.requestWhenInUseAuthorization()
    }

    func startTracking() {
        manager.startUpdatingLocation()
    }

    func locationManager(_ manager: CLLocationManager,
                         didUpdateLocations locations: [CLLocation]) {
        guard let latest = locations.last else { return }

        let latitude = latest.coordinate.latitude
        let longitude = latest.coordinate.longitude
        let accuracy = latest.horizontalAccuracy
        let altitude = latest.altitude

        locationUpdates?(latest)
    }

    func locationManager(_ manager: CLLocationManager,
                         didFailWithError error: Error) {
        print("Location error: \(error)")
    }
}
```

### Android: FusedLocationProvider
```kotlin
import com.google.android.gms.location.*

class LocationTracker(context: Context) {
    private val fusedLocationClient: FusedLocationProviderClient =
        LocationServices.getFusedLocationProviderClient(context)

    fun startLocationUpdates(callback: (Double, Double) -> Unit) {
        val locationRequest = LocationRequest.create().apply {
            interval = 10000
            fastestInterval = 5000
            priority = LocationRequest.PRIORITY_HIGH_ACCURACY
        }

        val locationCallback = object : LocationCallback() {
            override fun onLocationResult(result: LocationResult) {
                for (location in result.locations) {
                    callback(location.latitude, location.longitude)
                }
            }
        }

        if (ActivityCompat.checkSelfPermission(context,
                Manifest.permission.ACCESS_FINE_LOCATION)
            == PackageManager.PERMISSION_GRANTED) {
            fusedLocationClient.requestLocationUpdates(
                locationRequest, locationCallback, Looper.getMainLooper())
        }
    }

    fun getLastLocation(callback: (Location?) -> Unit) {
        if (ActivityCompat.checkSelfPermission(context,
                Manifest.permission.ACCESS_FINE_LOCATION)
            == PackageManager.PERMISSION_GRANTED) {
            fusedLocationClient.lastLocation.addOnSuccessListener { location ->
                callback(location)
            }
        }
    }
}
```

---

## 8. Geocoding & Reverse Geocoding

### iOS: CLGeocoder
```swift
import CoreLocation

class GeocodingController {
    let geocoder = CLGeocoder()

    func geocodeAddress(_ address: String) {
        geocoder.geocodeAddressString(address) { placemarks, error in
            guard let placemark = placemarks?.first else { return }

            if let location = placemark.location {
                print("Coordinates: \(location.coordinate)")
            }
            print("City: \(placemark.locality ?? "Unknown")")
            print("Country: \(placemark.country ?? "Unknown")")
        }
    }

    func reverseGeocode(latitude: CLLocationDegrees,
                        longitude: CLLocationDegrees) {
        let location = CLLocation(latitude: latitude, longitude: longitude)
        geocoder.reverseGeocodeLocation(location) { placemarks, error in
            guard let placemark = placemarks?.first else { return }

            let formatter = CNPostalAddressFormatter()
            if let address = placemark.postalAddress {
                let formattedAddress = formatter.string(from: address)
                print("Address: \(formattedAddress)")
            }
        }
    }
}
```

### Android: Geocoder
```kotlin
import android.location.Geocoder
import android.location.Address

class GeocodingService(context: Context) {
    private val geocoder = Geocoder(context, Locale.getDefault())

    fun geocodeAddress(addressString: String) {
        try {
            val addresses = geocoder.getFromLocationName(addressString, 1)
            if (addresses?.isNotEmpty() == true) {
                val address = addresses[0]
                println("Latitude: ${address.latitude}, Longitude: ${address.longitude}")
                println("City: ${address.locality}, Country: ${address.countryName}")
            }
        } catch (e: Exception) {
            Log.e("Geocoding", "Error", e)
        }
    }

    fun reverseGeocode(latitude: Double, longitude: Double) {
        try {
            val addresses = geocoder.getFromLocation(latitude, longitude, 1)
            if (addresses?.isNotEmpty() == true) {
                val address = addresses[0]
                val fullAddress = (0..address.maxAddressLineIndex)
                    .map { address.getAddressLine(it) }
                    .joinToString()
                println("Address: $fullAddress")
            }
        } catch (e: Exception) {
            Log.e("ReverseGeocoding", "Error", e)
        }
    }
}
```

---

## 9. Geofencing & Location Permissions

### iOS: Geofencing
```swift
class GeofenceManager: NSObject, CLLocationManagerDelegate {
    let manager = CLLocationManager()

    func createGeofence(latitude: CLLocationDegrees,
                        longitude: CLLocationDegrees,
                        radius: CLLocationDistance,
                        identifier: String) {
        let region = CLCircularRegion(center: CLLocationCoordinate2D(latitude: latitude,
                                                                      longitude: longitude),
                                      radius: radius,
                                      identifier: identifier)
        region.notifyOnEntry = true
        region.notifyOnExit = true

        manager.startMonitoring(for: region)
    }

    func locationManager(_ manager: CLLocationManager,
                         didEnterRegion region: CLRegion) {
        print("Entered region: \(region.identifier)")
        sendLocalNotification("Entered \(region.identifier)")
    }

    func locationManager(_ manager: CLLocationManager,
                         didExitRegion region: CLRegion) {
        print("Exited region: \(region.identifier)")
    }
}
```

### Android: Geofencing
```kotlin
import com.google.android.gms.location.Geofence
import com.google.android.gms.location.GeofencingRequest

class GeofenceHelper(context: Context) {
    fun addGeofence(latitude: Double, longitude: Double, radius: Float, id: String) {
        val geofence = Geofence.Builder()
            .setRequestId(id)
            .setCircularRegion(latitude, longitude, radius)
            .setExpirationDuration(Geofence.NEVER_EXPIRE)
            .setTransitionTypes(Geofence.GEOFENCE_TRANSITION_ENTER or
                               Geofence.GEOFENCE_TRANSITION_EXIT)
            .build()

        val request = GeofencingRequest.Builder()
            .setInitialTrigger(GeofencingRequest.INITIAL_TRIGGER_ENTER)
            .addGeofence(geofence)
            .build()

        // Use FusedLocationProviderClient.addGeofences()
    }
}
```

### Location Permissions
```swift
// iOS: Info.plist required keys
// NSLocationWhenInUseUsageDescription
// NSLocationAlwaysAndWhenInUseUsageDescription
// NSLocationAlwaysUsageDescription

// Android: AndroidManifest.xml
// <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
// <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
// <uses-permission android:name="android.permission.ACCESS_BACKGROUND_LOCATION" />
```

---

## 10. Background Location Tracking

### iOS: Background Modes
```swift
class BackgroundLocationTracker: NSObject, CLLocationManagerDelegate {
    let manager = CLLocationManager()

    func enableBackgroundTracking() {
        manager.allowsBackgroundLocationUpdates = true
        manager.pausesLocationUpdatesAutomatically = false
        manager.startUpdatingLocation()
    }

    func locationManager(_ manager: CLLocationManager,
                         didUpdateLocations locations: [CLLocation]) {
        guard let location = locations.last else { return }

        // Minimal battery impact
        if location.horizontalAccuracy < 100 {
            logLocation(location)
        }
    }
}

// Info.plist: UIBackgroundModes must include "location"
```

### Android: Background Services
```kotlin
class LocationService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val notification = createNotification()
        startForeground(NOTIFICATION_ID, notification)

        startLocationUpdates()
        return START_STICKY
    }

    private fun startLocationUpdates() {
        val locationRequest = LocationRequest.create().apply {
            interval = 30000 // 30 seconds
            priority = LocationRequest.PRIORITY_HIGH_ACCURACY
        }

        // Implementation with FusedLocationProviderClient
    }
}
```

---

## 11. Custom Map Annotations & Overlays

### iOS: Custom Annotations
```swift
class CustomAnnotation: NSObject, MKAnnotation {
    @objc dynamic var coordinate: CLLocationCoordinate2D
    let title: String?
    let subtitle: String?
    let image: UIImage?

    init(coordinate: CLLocationCoordinate2D, title: String?, image: UIImage?) {
        self.coordinate = coordinate
        self.title = title
        self.subtitle = nil
        self.image = image
    }
}

extension MapViewController: MKMapViewDelegate {
    func mapView(_ mapView: MKMapView,
                 viewFor annotation: MKAnnotation) -> MKAnnotationView? {
        guard let annotation = annotation as? CustomAnnotation else { return nil }

        let view = mapView.dequeueReusableAnnotationView(withIdentifier: "custom") ??
                   MKAnnotationView(annotation: annotation, reuseIdentifier: "custom")
        view.image = annotation.image
        view.centerOffset = CGPoint(x: 0, y: -25)
        return view
    }
}
```

### Android: Custom Map Objects
```kotlin
fun addCustomMarker(googleMap: GoogleMap, latlng: LatLng, bitmap: Bitmap) {
    val markerOptions = MarkerOptions()
        .position(latlng)
        .icon(BitmapDescriptorFactory.fromBitmap(bitmap))
        .anchor(0.5f, 0.5f)
        .title("Custom Marker")

    googleMap.addMarker(markerOptions)
}

fun addPolygon(googleMap: GoogleMap) {
    val polygon = googleMap.addPolygon(PolygonOptions()
        .add(
            LatLng(-33.852, 151.211),
            LatLng(-33.857, 151.215),
            LatLng(-33.860, 151.220)
        )
        .fillColor(Color.argb(50, 0, 0, 255))
        .strokeColor(Color.BLUE)
        .strokeWidth(3f))
}
```

---

## 12. Indoor Positioning Basics

### iOS: Indoor Maps (MapKit)
```swift
class IndoorMapController: UIViewController {
    func enableIndoorMaps() {
        mapView.showsBuildings = true

        // Apple Maps supports some venues with indoor routing
        let request = MKLocalSearch.Request()
        request.naturalLanguageQuery = "Apple Park"

        let search = MKLocalSearch(request: request)
        search.start { response, error in
            guard let mapItem = response?.mapItems.first else { return }

            let region = MKCoordinateRegion(
                center: mapItem.placemark.coordinate,
                span: MKCoordinateSpan(latitudeDelta: 0.02, longitudeDelta: 0.02)
            )
            self.mapView.setRegion(region, animated: true)
        }
    }
}
```

### Android: Indoor Maps (Google Maps)
```kotlin
class IndoorMapActivity : AppCompatActivity() {
    private lateinit var googleMap: GoogleMap

    private fun setupIndoorMap() {
        googleMap.isIndoorEnabled = true

        val buildingLocation = LatLng(40.7128, -74.0060)
        googleMap.moveCamera(CameraUpdateFactory.newLatLngZoom(buildingLocation, 18f))
    }
}
```

### BLE-based Indoor Positioning
```swift
import CoreLocation

class BLEIndoorPositioning: NSObject, CLLocationManagerDelegate {
    let locationManager = CLLocationManager()
    var beaconRegions: [CLBeaconIdentityConstraint] = []

    func startBeaconMonitoring() {
        let constraint = CLBeaconIdentityConstraint(
            uuid: UUID(uuidString: "12345678-1234-1234-1234-123456789012")!)

        let region = CLBeaconRegion(beaconIdentityConstraint: constraint,
                                    identifier: "MyBeacon")
        locationManager.startRangingBeacons(satisfying: constraint)
    }

    func locationManager(_ manager: CLLocationManager,
                         didRangeBeacons beacons: [CLBeacon],
                         in region: CLBeaconRegion) {
        for beacon in beacons {
            let accuracy = beacon.accuracy
            // Trilateration with multiple beacons
            print("Distance estimate: \(accuracy) meters")
        }
    }
}
```

---

## Key Frameworks Summary

| Platform | AR | Camera | Maps | Location |
|----------|----|---------|----- |----------|
| iOS | ARKit, RealityKit | AVFoundation | MapKit | Core Location |
| Android | ARCore | CameraX | Google Maps | FusedLocationProvider |
| Cross-Platform | React Native AR | React Native Camera | react-native-maps | react-native-geolocation |

## Best Practices

- Request permissions explicitly and explain usage to users
- Handle background location carefully for battery efficiency
- Cache map tiles and geocoding results when possible
- Use appropriate accuracy levels for location requests
- Test AR experiences on real devices
- Implement proper error handling for all location/camera access
- Consider privacy implications of tracking and data collection
