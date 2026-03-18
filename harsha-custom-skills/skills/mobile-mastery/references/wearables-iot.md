# Wearables & IoT Development Reference

## Table of Contents
- [1. watchOS - SwiftUI for Apple Watch](#1-watchos---swiftui-for-apple-watch)
- [2. Wear OS - Compose for Wear OS](#2-wear-os---compose-for-wear-os)
- [3. HealthKit (iOS)](#3-healthkit-ios)
- [4. Health Connect (Android)](#4-health-connect-android)
- [5. Bluetooth Low Energy (BLE)](#5-bluetooth-low-energy-ble)
- [6. IoT Protocols](#6-iot-protocols)
- [7. NFC](#7-nfc)
- [8. WidgetKit (iOS)](#8-widgetkit-ios)
- [9. Android App Widgets / Glance](#9-android-app-widgets--glance)
- [10. Smart Home - HomeKit Basics](#10-smart-home---homekit-basics)

## 1. watchOS - SwiftUI for Apple Watch

### Basic Watch App Structure
```swift
import SwiftUI

@main
struct WatchApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}

struct ContentView: View {
    @State private var heartRate = 72

    var body: some View {
        VStack(spacing: 12) {
            Text("Heart Rate")
                .font(.caption)
                .foregroundColor(.secondary)

            Text("\(heartRate)")
                .font(.system(size: 36, weight: .bold))

            Button(action: { heartRate += 1 }) {
                Label("Refresh", systemImage: "arrow.clockwise")
                    .font(.caption2)
            }
            .buttonStyle(.bordered)
        }
        .padding()
    }
}
```

### Watch Complications
```swift
import ClockKit

struct FitnessProvider: CLKComplicationDataSource {
    func getCurrentTimelineEntry(
        for complication: CLKComplication,
        withHandler handler: @escaping (CLKComplicationTimelineEntry?) -> Void
    ) {
        let entry = CLKComplicationTimelineEntry(
            date: Date(),
            complicationTemplate: createTemplate(for: complication)
        )
        handler(entry)
    }

    private func createTemplate(for complication: CLKComplication) -> CLKComplicationTemplate {
        let progress: Float = 0.65

        switch complication.family {
        case .circularSmall:
            return CLKComplicationTemplateCircularSmallRingGauge(
                gaugeProvider: CLKSimpleGaugeProvider(
                    style: .ring,
                    gaugeColors: [.green],
                    gaugePositions: [NSNumber(value: progress)]
                )
            )
        case .modularSmall:
            return CLKComplicationTemplateModularSmallSimpleText(
                textProvider: CLKSimpleTextProvider(text: "65%")
            )
        default:
            return CLKComplicationTemplateGraphicCircularGauge(
                gaugeProvider: CLKSimpleGaugeProvider(
                    style: .ring,
                    gaugeColors: [.green],
                    gaugePositions: [NSNumber(value: progress)]
                ),
                outerTextProvider: CLKSimpleTextProvider(text: "Walk")
            )
        }
    }
}
```

### Workout Sessions
```swift
import HealthKit

class WorkoutManager: NSObject, ObservableObject {
    @Published var isRunning = false
    @Published var calories: Double = 0
    @Published var distance: Double = 0

    private var session: HKWorkoutSession?
    private let healthStore = HKHealthStore()

    func startWorkout() {
        let config = HKWorkoutConfiguration()
        config.activityType = .running
        config.locationType = .outdoor

        do {
            session = try HKWorkoutSession(
                healthStore: healthStore,
                configuration: config
            )
            session?.delegate = self
            try session?.startActivity()
            isRunning = true
        } catch {
            print("Failed to start workout: \(error)")
        }
    }

    func stopWorkout() {
        session?.end()
        isRunning = false
    }
}

extension WorkoutManager: HKWorkoutSessionDelegate {
    func workoutSession(
        _ workoutSession: HKWorkoutSession,
        didChangeTo newState: HKWorkoutSessionState,
        from oldState: HKWorkoutSessionState,
        date: Date
    ) {
        DispatchQueue.main.async {
            self.isRunning = newState == .running
        }
    }

    func workoutSession(
        _ workoutSession: HKWorkoutSession,
        didFailWithError error: Error
    ) {
        print("Workout session failed: \(error)")
    }
}
```

### WatchConnectivity
```swift
import WatchConnectivity

class WatchConnectivityManager: NSObject, ObservableObject {
    static let shared = WatchConnectivityManager()
    @Published var receivedMessage: String = ""

    override init() {
        super.init()
        if WCSession.isSupported() {
            WCSession.default.delegate = self
            WCSession.default.activate()
        }
    }

    func sendUserInfo(data: [String: Any]) {
        WCSession.default.transferUserInfo(data)
    }

    func sendMessage(message: [String: Any]) {
        guard WCSession.default.isReachable else { return }
        WCSession.default.sendMessage(message) { response in
            print("Watch responded: \(response)")
        }
    }
}

extension WatchConnectivityManager: WCSessionDelegate {
    func session(
        _ session: WCSession,
        activationDidCompleteWith activationState: WCSessionActivationState,
        error: Error?
    ) {
        print("WC Session activated: \(activationState.rawValue)")
    }

    func sessionDidBecomeInactive(_ session: WCSession) {}
    func sessionDidDeactivate(_ session: WCSession) {}

    func session(_ session: WCSession, didReceiveMessage message: [String : Any]) {
        DispatchQueue.main.async {
            self.receivedMessage = message["text"] as? String ?? ""
        }
    }
}
```

---

## 2. Wear OS - Compose for Wear OS

### Basic Wear OS Screen
```kotlin
@Composable
fun HeartRateScreen() {
    var heartRate by remember { mutableStateOf(72) }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.Black)
            .padding(8.dp),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            modifier = Modifier.fillMaxWidth()
        ) {
            Text(
                text = "Heart Rate",
                style = MaterialTheme.typography.labelSmall,
                color = Color.Gray
            )
            Text(
                text = "$heartRate",
                style = MaterialTheme.typography.displayLarge,
                color = Color.Green,
                modifier = Modifier.padding(vertical = 8.dp)
            )
            Button(onClick = { heartRate += 1 }) {
                Text("Refresh", style = MaterialTheme.typography.labelSmall)
            }
        }
    }
}
```

### Wear OS Tiles
```kotlin
class FitnessTileService : TileService() {
    override fun onTileRequest(requestParams: RequestParams, callback: Consumer<Tile>) {
        val tile = Tile.Builder()
            .setResourcesVersion("1")
            .setTimeline(Timeline.Builder()
                .addTimelineEntry(TimelineEntry.Builder()
                    .setLayout(buildLayout())
                    .build())
                .build())
            .build()
        callback.accept(tile)
    }

    private fun buildLayout(): Layout {
        return Layout.Builder()
            .setRoot(Column.Builder()
                .setWidth(expand())
                .setHeight(expand())
                .setHorizontalAlignment(HORIZONTAL_ALIGN_CENTER)
                .setVerticalAlignment(VERTICAL_ALIGN_CENTER)
                .addChild(Text.Builder()
                    .setText("Steps: 8,432")
                    .setFontStyle(FontStyle.Builder()
                        .setSize(16)
                        .build())
                    .build())
                .addChild(Text.Builder()
                    .setText("Goal: 10,000")
                    .setFontStyle(FontStyle.Builder()
                        .setSize(12)
                        .setColor(0xFF888888.toInt())
                        .build())
                    .build())
                .build())
            .build()
    }
}
```

### Health Services
```kotlin
class HealthManager(context: Context) {
    private val healthClient = HealthServicesClient(context)

    suspend fun getHeartRate(): Result<Double> = try {
        val capabilities = healthClient.getCapabilities()
        val heartRateSupported = capabilities.supportedDataTypes.contains(
            DataType.HEART_RATE_BPM
        )

        if (heartRateSupported) {
            val measurements = healthClient.readRecords(ReadRecordsRequest(
                dataTypes = setOf(DataType.HEART_RATE_BPM),
                timeRangeFilter = TimeRangeFilter.between(
                    startTime = Instant.now().minus(1, ChronoUnit.HOURS),
                    endTime = Instant.now()
                )
            ))
            Result.success(measurements.records.lastOrNull()?.samples?.lastOrNull()?.value ?: 0.0)
        } else {
            Result.failure(Exception("Heart rate not supported"))
        }
    } catch (e: Exception) {
        Result.failure(e)
    }
}
```

---

## 3. HealthKit (iOS)

### HealthKit Setup & Permissions
```swift
import HealthKit

class HealthKitManager {
    let healthStore = HKHealthStore()

    func requestPermissions(completion: @escaping (Bool, Error?) -> Void) {
        let typesToRead: Set<HKObjectType> = [
            HKObjectType.quantityType(forIdentifier: .stepCount)!,
            HKObjectType.quantityType(forIdentifier: .heartRate)!,
            HKObjectType.workoutType()
        ]

        let typesToWrite: Set<HKSampleType> = [
            HKObjectType.quantityType(forIdentifier: .stepCount)!,
            HKObjectType.workoutType()
        ]

        healthStore.requestAuthorization(
            toShare: typesToWrite,
            read: typesToRead
        ) { success, error in
            completion(success, error)
        }
    }

    func getStepCount(for date: Date, completion: @escaping (Int?) -> Void) {
        let stepsType = HKQuantityType.quantityType(forIdentifier: .stepCount)!
        let startOfDay = Calendar.current.startOfDay(for: date)
        let predicate = HKQuery.predicateForSamples(
            withStart: startOfDay,
            end: Date(),
            options: .strictStartDate
        )

        let query = HKStatisticsQuery(
            quantityType: stepsType,
            quantitySamplePredicate: predicate,
            options: .cumulativeSum
        ) { _, statistics, _ in
            let count = statistics?.sumQuantity()?.doubleValue(for: HKUnit.count())
            DispatchQueue.main.async {
                completion(Int(count ?? 0))
            }
        }

        healthStore.execute(query)
    }

    func getHeartRate(for date: Date, completion: @escaping ([Int]) -> Void) {
        let heartRateType = HKQuantityType.quantityType(forIdentifier: .heartRate)!
        let startOfDay = Calendar.current.startOfDay(for: date)
        let predicate = HKQuery.predicateForSamples(
            withStart: startOfDay,
            end: Date(),
            options: .strictStartDate
        )

        let query = HKSampleQuery(
            sampleType: heartRateType,
            predicate: predicate,
            limit: HKObjectQueryNoLimit,
            sortDescriptors: [NSSortDescriptor(key: HKSampleSortIdentifierStartDate, ascending: false)]
        ) { _, samples, _ in
            let heartRates = samples?.compactMap { sample in
                Int(sample.quantity.doubleValue(for: HKUnit(from: "count/min")))
            } ?? []
            DispatchQueue.main.async {
                completion(heartRates)
            }
        }

        healthStore.execute(query)
    }

    func saveWorkout(
        type: HKWorkoutActivityType,
        duration: TimeInterval,
        energy: Double
    ) {
        let now = Date()
        let startDate = now.addingTimeInterval(-duration)

        let workout = HKWorkout(
            activityType: type,
            start: startDate,
            end: now,
            duration: duration,
            totalEnergyBurned: HKQuantity(unit: .kilocalorie(), doubleValue: energy),
            totalDistance: nil,
            metadata: nil
        )

        healthStore.save(workout) { success, error in
            if success {
                print("Workout saved successfully")
            } else if let error = error {
                print("Error saving workout: \(error)")
            }
        }
    }
}
```

---

## 4. Health Connect (Android)

### Health Connect Read/Write
```kotlin
class HealthConnectManager(context: Context) {
    private val healthConnectClient = HealthConnectClient.getOrCreate(context)

    suspend fun readSteps(date: LocalDate): Int = try {
        val response = healthConnectClient.readRecords(
            ReadRecordsRequest(
                recordTypes = setOf(StepsRecord::class),
                timeRangeFilter = TimeRangeFilter.between(
                    startTime = date.atStartOfDay().toInstant(ZoneOffset.UTC),
                    endTime = date.plusDays(1).atStartOfDay().toInstant(ZoneOffset.UTC)
                )
            )
        )
        response.records.sumOf { (it as StepsRecord).count }.toInt()
    } catch (e: Exception) {
        0
    }

    suspend fun writeHeartRate(heartRate: Int, timestamp: Instant) = try {
        val heartRateRecord = HeartRateRecord(
            startTime = timestamp,
            endTime = timestamp,
            heartRate = heartRate
        )
        healthConnectClient.insertRecords(listOf(heartRateRecord))
        true
    } catch (e: Exception) {
        false
    }

    suspend fun getAggregatedSteps(dateRange: Pair<LocalDate, LocalDate>): Int = try {
        val response = healthConnectClient.aggregate(
            AggregateRequest(
                metrics = setOf(Steps),
                timeRangeFilter = TimeRangeFilter.between(
                    startTime = dateRange.first.atStartOfDay().toInstant(ZoneOffset.UTC),
                    endTime = dateRange.second.plusDays(1).atStartOfDay().toInstant(ZoneOffset.UTC)
                )
            )
        )
        response[Steps]?.toInt() ?: 0
    } catch (e: Exception) {
        0
    }
}
```

---

## 5. Bluetooth Low Energy (BLE)

### Core Bluetooth (iOS)
```swift
import CoreBluetooth

class BLEManager: NSObject, ObservableObject {
    @Published var discoveredDevices: [CBPeripheral] = []
    @Published var isScanning = false

    private var centralManager: CBCentralManager!
    private var connectedPeripheral: CBPeripheral?

    override init() {
        super.init()
        centralManager = CBCentralManager(delegate: self, queue: .main)
    }

    func startScanning() {
        isScanning = true
        centralManager.scanForPeripherals(
            withServices: nil,
            options: [CBCentralManagerScanOptionAllowDuplicatesKey: false]
        )
    }

    func stopScanning() {
        isScanning = false
        centralManager.stopScan()
    }

    func connect(to peripheral: CBPeripheral) {
        connectedPeripheral = peripheral
        centralManager.connect(peripheral, options: nil)
    }

    func disconnect() {
        if let peripheral = connectedPeripheral {
            centralManager.cancelPeripheralConnection(peripheral)
        }
    }
}

extension BLEManager: CBCentralManagerDelegate {
    func centralManagerDidUpdateState(_ central: CBCentralManager) {
        switch central.state {
        case .poweredOn:
            print("Bluetooth is ready")
        case .poweredOff:
            print("Bluetooth is off")
        default:
            print("Bluetooth unavailable")
        }
    }

    func centralManager(
        _ central: CBCentralManager,
        didDiscover peripheral: CBPeripheral,
        advertisementData: [String : Any],
        rssi RSSI: NSNumber
    ) {
        if !discoveredDevices.contains(peripheral) {
            discoveredDevices.append(peripheral)
        }
    }

    func centralManager(_ central: CBCentralManager, didConnect peripheral: CBPeripheral) {
        peripheral.delegate = self
        peripheral.discoverServices(nil)
    }
}

extension BLEManager: CBPeripheralDelegate {
    func peripheral(_ peripheral: CBPeripheral, didDiscoverServices error: Error?) {
        guard let services = peripheral.services else { return }
        for service in services {
            peripheral.discoverCharacteristics(nil, for: service)
        }
    }
}
```

### Android BLE
```kotlin
class AndroidBLEManager(context: Context) : BluetoothAdapter.LeScanCallback {
    private val bluetoothAdapter = BluetoothManager(context).adapter
    private val discoveredDevices = mutableListOf<BluetoothDevice>()

    fun startScan() {
        bluetoothAdapter?.startLeScan(this)
    }

    fun stopScan() {
        bluetoothAdapter?.stopLeScan(this)
    }

    fun connectToDevice(device: BluetoothDevice, context: Context) {
        val gatt = device.connectGatt(context, false, BluetoothGattCallback())
    }

    override fun onLeScan(device: BluetoothDevice?, rssi: Int, scanRecord: ByteArray?) {
        device?.let {
            if (!discoveredDevices.contains(it)) {
                discoveredDevices.add(it)
                println("Found device: ${it.name} (${it.address})")
            }
        }
    }

    private inner class BluetoothGattCallback : BluetoothGattCallback() {
        override fun onConnectionStateChange(gatt: BluetoothGatt, status: Int, newState: Int) {
            if (newState == BluetoothProfile.STATE_CONNECTED) {
                gatt.discoverServices()
            }
        }

        override fun onServicesDiscovered(gatt: BluetoothGatt, status: Int) {
            val service = gatt.getService(UUID.fromString("180D"))
            val characteristic = service?.getCharacteristic(UUID.fromString("2A37"))
            characteristic?.let {
                gatt.readCharacteristic(it)
            }
        }

        override fun onCharacteristicRead(gatt: BluetoothGatt, characteristic: BluetoothGattCharacteristic, status: Int) {
            val value = characteristic.value
            println("Heart Rate: ${value[1]}")
        }
    }
}
```

### React Native BLE (react-native-ble-plx)
```typescript
import { BleManager } from 'react-native-ble-plx';

const manager = new BleManager();

export class BLEService {
    scanForDevices = (callback: (devices: any[]) => void) => {
        const subscription = manager.onStateChange((state) => {
            if (state === 'PoweredOn') {
                this.performScan(callback);
                subscription.remove();
            }
        }, true);
    };

    private performScan = (callback: (devices: any[]) => void) => {
        const devices: any[] = [];
        manager.startDeviceScan(null, null, (error, device) => {
            if (error) return;

            if (device && !devices.find(d => d.id === device.id)) {
                devices.push(device);
                callback(devices);
            }
        });
    };

    connectToDevice = async (deviceId: string) => {
        try {
            const device = await manager.connectToDevice(deviceId);
            await device.discoverAllServicesAndCharacteristics();
            return device;
        } catch (error) {
            console.error('Connection failed:', error);
        }
    };

    readHeartRate = async (device: any) => {
        const characteristic = await device.readCharacteristicForService(
            '180D',
            '2A37'
        );
        const value = characteristic.value;
        return Buffer.from(value, 'base64')[1];
    };
}
```

---

## 6. IoT Protocols

### MQTT Implementation
```swift
import CocoaMQTT

class MQTTManager {
    let mqtt = CocoaMQTT(clientID: "ios-device-\(UUID().uuidString)", host: "broker.mqtt.com", port: 1883)

    func setupMQTT() {
        mqtt.delegate = self
        mqtt.connect()
    }

    func publishHeartRate(_ value: Int) {
        let topic = "health/heart-rate/\(UIDevice.current.identifierForVendor?.uuidString ?? "unknown")"
        let message = """
        {
            "value": \(value),
            "timestamp": "\(ISO8601DateFormatter().string(from: Date()))"
        }
        """
        mqtt.publish(topic, withString: message, qos: .atLeastOnce)
    }

    func subscribeToCommands() {
        mqtt.subscribe("device/commands/+", qos: .atLeastOnce)
    }
}

extension MQTTManager: CocoaMQTTDelegate {
    func mqtt(_ mqtt: CocoaMQTT, didConnectAck ack: CocoaMQTTConnAck) {
        print("MQTT Connected")
        subscribeToCommands()
    }

    func mqtt(_ mqtt: CocoaMQTT, didReceiveMessage message: CocoaMQTTMessage, id: UInt16) {
        print("Received: \(message.topic) - \(message.string ?? "")")
    }
}
```

### Matter/Thread (iOS)
```swift
import Matter

class MatterController {
    let matterController = MTRSetupPayloadParser()

    func setupMatterDevice(qrCode: String) throws {
        let setupPayload = try matterController.parseQRCode(qrCode)
        print("Setup Code: \(setupPayload.setupPasscode)")

        // Provision device
        let deviceController = MTRDeviceController(initParams: MTRDeviceControllerStartupParams())
        try deviceController?.start()
    }

    func controlLightBulb(deviceId: UInt64, isOn: Bool) {
        let params = MTROnOffClusterToggleParams()
        let device = MTRDevice(nodeID: NSNumber(value: deviceId), controller: nil)

        device?.invokeCommand(
            with: params,
            completion: { response, error in
                if let error = error {
                    print("Command failed: \(error)")
                }
            }
        )
    }
}
```

### MQTT (Android)
```kotlin
class MQTTManager(context: Context) {
    private val client = MqttAndroidClient(
        context,
        "tcp://broker.mqtt.com:1883",
        MqttClient.generateClientId()
    )

    fun connect() {
        val options = MqttConnectOptions().apply {
            isCleanSession = true
            isAutomaticReconnect = true
        }

        client.connect(options, null, object : IMqttActionListener {
            override fun onSuccess(asyncActionToken: IMqttToken?) {
                println("Connected to MQTT")
                subscribe("device/commands/+")
            }

            override fun onFailure(asyncActionToken: IMqttToken?, exception: Throwable?) {
                println("Failed to connect: ${exception?.message}")
            }
        })
    }

    fun publishHeartRate(heartRate: Int) {
        val topic = "health/heart-rate/${deviceId()}"
        val payload = """
            {
                "value": $heartRate,
                "timestamp": "${System.currentTimeMillis()}"
            }
        """.toByteArray()

        client.publish(topic, payload, 1, false)
    }

    private fun subscribe(topic: String) {
        client.subscribe(topic, 1, null, object : IMqttActionListener {
            override fun onSuccess(asyncActionToken: IMqttToken?) {
                println("Subscribed to $topic")
            }

            override fun onFailure(asyncActionToken: IMqttToken?, exception: Throwable?) {}
        })
    }
}
```

---

## 7. NFC

### Core NFC (iOS)
```swift
import CoreNFC

class NFCManager: NSObject, ObservableObject {
    @Published var detectedTag: String?

    func scanNFC() {
        let session = NFCNDEFReaderSession(delegate: self, queue: .main, invalidateAfterFirstRead: false)
        session?.begin()
    }

    func writeNFC(message: String) {
        let session = NFCNDEFReaderSession(delegate: self, queue: .main, invalidateAfterFirstRead: false)
        session?.begin()
    }
}

extension NFCManager: NFCNDEFReaderSessionDelegate {
    func readerSession(
        _ session: NFCNDEFReaderSession,
        didInvalidateWithError error: Error
    ) {
        print("NFC session error: \(error)")
    }

    func readerSession(
        _ session: NFCNDEFReaderSession,
        didDetectNDEFs messages: [NFCNDEFMessage]
    ) {
        for message in messages {
            for record in message.records {
                if let text = String(data: record.payload, encoding: .utf8) {
                    DispatchQueue.main.async {
                        self.detectedTag = text
                    }
                }
            }
        }
    }
}
```

### Android NFC
```kotlin
class NFCManager(context: Context) {
    private val nfcAdapter = NfcAdapter.getDefaultAdapter(context)

    fun readNFC(intent: Intent): String? {
        val tag: Tag? = intent.getParcelableExtra(NfcAdapter.EXTRA_TAG)
        tag?.let {
            val ndef = Ndef.get(it)
            val ndefMessage = ndef?.ndefMessage

            ndefMessage?.records?.forEach { record ->
                val message = String(record.payload)
                return message
            }
        }
        return null
    }

    fun writeNFC(intent: Intent, message: String): Boolean {
        val tag: Tag? = intent.getParcelableExtra(NfcAdapter.EXTRA_TAG)
        tag?.let {
            val ndefRecord = NdefRecord.createTextRecord("en", message)
            val ndefMessage = NdefMessage(arrayOf(ndefRecord))
            val ndef = Ndef.get(it)

            return try {
                ndef?.connect()
                ndef?.writeNdefMessage(ndefMessage)
                ndef?.close()
                true
            } catch (e: Exception) {
                false
            }
        }
        return false
    }

    fun enableForegroundDispatch(activity: Activity, pendingIntent: PendingIntent) {
        nfcAdapter?.enableForegroundDispatch(activity, pendingIntent, null, null)
    }
}
```

---

## 8. WidgetKit (iOS)

### TimelineProvider & Widget
```swift
import WidgetKit
import SwiftUI

struct FitnessEntry: TimelineEntry {
    let date: Date
    let stepCount: Int
    let heartRate: Int
}

struct FitnessProvider: TimelineProvider {
    func placeholder(in context: Context) -> FitnessEntry {
        FitnessEntry(date: Date(), stepCount: 8432, heartRate: 72)
    }

    func getSnapshot(in context: Context, completion: @escaping (FitnessEntry) -> Void) {
        let entry = FitnessEntry(date: Date(), stepCount: 8432, heartRate: 72)
        completion(entry)
    }

    func getTimeline(in context: Context, completion: @escaping (Timeline<FitnessEntry>) -> Void) {
        var entries: [FitnessEntry] = []
        let currentDate = Date()

        for hourOffset in 0 ..< 24 {
            let entryDate = Calendar.current.date(byAdding: .hour, value: hourOffset, to: currentDate)!
            let entry = FitnessEntry(
                date: entryDate,
                stepCount: Int.random(in: 8000...10000),
                heartRate: Int.random(in: 60...100)
            )
            entries.append(entry)
        }

        let timeline = Timeline(entries: entries, policy: .atEnd)
        completion(timeline)
    }
}

struct FitnessWidgetView: View {
    var entry: FitnessProvider.Entry

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text("Steps")
                    .font(.caption)
                    .foregroundColor(.secondary)
                Spacer()
                Text("\(entry.stepCount)")
                    .font(.headline)
            }

            HStack {
                Text("Heart Rate")
                    .font(.caption)
                    .foregroundColor(.secondary)
                Spacer()
                Text("\(entry.heartRate) BPM")
                    .font(.headline)
            }

            ProgressView(value: Double(entry.stepCount) / 10000)
                .tint(.green)
        }
        .padding()
        .background(Color(.systemBackground))
    }
}

@main
struct FitnessWidget: Widget {
    let kind: String = "FitnessWidget"

    var body: some WidgetConfiguration {
        StaticConfiguration(
            kind: kind,
            provider: FitnessProvider()
        ) { entry in
            FitnessWidgetView(entry: entry)
        }
        .configurationDisplayName("Fitness")
        .description("View your daily fitness stats")
        .supportedFamilies([.systemSmall, .systemMedium])
    }
}
```

---

## 9. Android App Widgets / Glance

### App Widget with RemoteViews
```kotlin
class FitnessWidgetProvider : AppWidgetProvider() {
    override fun onUpdate(context: Context, appWidgetManager: AppWidgetManager, appWidgetIds: IntArray) {
        for (appWidgetId in appWidgetIds) {
            updateAppWidget(context, appWidgetManager, appWidgetId)
        }
    }

    private fun updateAppWidget(context: Context, appWidgetManager: AppWidgetManager, appWidgetId: Int) {
        val views = RemoteViews(context.packageName, R.layout.widget_fitness)
        views.setTextViewText(R.id.step_count, "8,432")
        views.setTextViewText(R.id.heart_rate, "72 BPM")
        views.setProgressBar(R.id.progress, 10000, 8432, false)

        appWidgetManager.updateAppWidget(appWidgetId, views)
    }
}
```

### Glance Widget (Modern Approach)
```kotlin
class FitnessGlanceWidget : GlanceAppWidget() {
    override suspend fun provideGlance(context: Context, id: GlanceId) {
        provideContent {
            FitnessWidgetContent()
        }
    }
}

@Composable
private fun FitnessWidgetContent() {
    Column(
        modifier = GlanceModifier
            .fillMaxSize()
            .background(ColorProvider(R.color.widget_bg))
            .padding(16.dp)
    ) {
        Text(
            text = "Steps",
            modifier = GlanceModifier.padding(bottom = 4.dp),
            style = TextStyle(fontSize = 12.sp, color = ColorProvider(R.color.text_secondary))
        )
        Text(
            text = "8,432",
            modifier = GlanceModifier.padding(bottom = 8.dp),
            style = TextStyle(fontSize = 28.sp, fontWeight = FontWeight.Bold)
        )

        Spacer(modifier = GlanceModifier.height(8.dp))

        Text(
            text = "Heart Rate",
            modifier = GlanceModifier.padding(bottom = 4.dp),
            style = TextStyle(fontSize = 12.sp, color = ColorProvider(R.color.text_secondary))
        )
        Text(
            text = "72 BPM",
            style = TextStyle(fontSize = 20.sp, fontWeight = FontWeight.Bold)
        )
    }
}
```

---

## 10. Smart Home - HomeKit Basics

### HomeKit Setup (iOS)
```swift
import HomeKit

class HomeKitManager: NSObject, ObservableObject {
    @Published var accessories: [HMAccessory] = []
    let homeManager = HMHomeManager()

    override init() {
        super.init()
        homeManager.delegate = self
    }

    func discoverAccessories() {
        homeManager.addAndSetupAccessories { error in
            if let error = error {
                print("Discovery error: \(error)")
            }
        }
    }

    func toggleLight(accessory: HMAccessory, isOn: Bool) {
        guard let lightService = accessory.services.first(where: { $0.serviceType == HMServiceTypeLightbulb }) else { return }
        guard let powerCharacteristic = lightService.characteristics.first(where: { $0.characteristicType == HMCharacteristicTypePower }) else { return }

        powerCharacteristic.writeValue(isOn) { error in
            if let error = error {
                print("Failed to toggle light: \(error)")
            } else {
                print("Light toggled successfully")
            }
        }
    }

    func getTemperature(accessory: HMAccessory) -> Double? {
        guard let thermoService = accessory.services.first(where: { $0.serviceType == HMServiceTypeThermostat }) else { return nil }
        guard let tempCharacteristic = thermoService.characteristics.first(where: { $0.characteristicType == HMCharacteristicTypeCurrentTemperature }) else { return nil }

        return tempCharacteristic.value as? Double
    }

    func setTargetTemperature(accessory: HMAccessory, temperature: Double) {
        guard let thermoService = accessory.services.first(where: { $0.serviceType == HMServiceTypeThermostat }) else { return }
        guard let targetTempCharacteristic = thermoService.characteristics.first(where: { $0.characteristicType == HMCharacteristicTypeTargetTemperature }) else { return }

        targetTempCharacteristic.writeValue(temperature) { error in
            if let error = error {
                print("Failed to set temperature: \(error)")
            }
        }
    }
}

extension HomeKitManager: HMHomeManagerDelegate {
    func homeManagerDidUpdateHomes(_ manager: HMHomeManager) {
        var allAccessories: [HMAccessory] = []
        for home in manager.homes {
            allAccessories.append(contentsOf: home.accessories)
        }
        DispatchQueue.main.async {
            self.accessories = allAccessories
        }
    }
}
```

---

## References

- **watchOS**: [Apple Watch Developer](https://developer.apple.com/watchos/)
- **Wear OS**: [Google Wear OS](https://developer.android.com/wear)
- **HealthKit**: [HealthKit Framework](https://developer.apple.com/healthkit/)
- **Health Connect**: [Android Health Connect](https://developer.android.com/health-and-fitness/health-connect)
- **Core Bluetooth**: [Core Bluetooth Framework](https://developer.apple.com/documentation/corebluetooth)
- **Matter**: [Matter Connectivity](https://csa-iot.org/csa_iot_zb_product/matter/)
- **HomeKit**: [HomeKit Framework](https://developer.apple.com/homekit/)
- **WidgetKit**: [WidgetKit Documentation](https://developer.apple.com/documentation/widgetkit)
- **Glance**: [Glance for Wear OS](https://developer.android.com/wear/glance)
