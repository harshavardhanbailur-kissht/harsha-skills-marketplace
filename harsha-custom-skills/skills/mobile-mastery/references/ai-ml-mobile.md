# Comprehensive AI/ML Mobile Development Reference

## Table of Contents
- [1. Core ML (iOS)](#1-core-ml-ios)
- [2. TensorFlow Lite (Cross-Platform)](#2-tensorflow-lite-cross-platform)
- [3. ML Kit (Android)](#3-ml-kit-android)
- [4. On-Device NLP](#4-on-device-nlp)
- [5. Recommendation Engines](#5-recommendation-engines)
- [6. Computer Vision (Detection & Segmentation)](#6-computer-vision-detection--segmentation)
- [7. Audio & Speech Processing](#7-audio--speech-processing)

## 1. Core ML (iOS)

### Image Classification with Core ML

Core ML enables on-device inference for trained models. It supports models from TensorFlow, PyTorch, scikit-learn, and XGBoost.

```swift
import CoreML
import Vision

// Load and use Core ML model
func classifyImage(_ image: UIImage) {
    guard let model = try? MobileNetV2(configuration: MLModelConfiguration()) else {
        print("Failed to load model")
        return
    }

    // Convert UIImage to CVPixelBuffer
    guard let pixelBuffer = image.toCVPixelBuffer() else {
        return
    }

    do {
        let input = MobileNetV2Input(image: pixelBuffer)
        let output = try model.prediction(input: input)

        // Get classification results
        if let classLabel = output.classLabel {
            print("Classified as: \(classLabel)")
            print("Confidence: \(output.classLabelProbs[classLabel] ?? 0)")
        }
    } catch {
        print("Prediction error: \(error)")
    }
}

// Helper to convert UIImage to CVPixelBuffer
extension UIImage {
    func toCVPixelBuffer() -> CVPixelBuffer? {
        let attrs = [
            kCVPixelBufferCGImageCompatibilityKey: kCFBooleanTrue,
            kCVPixelBufferCGBitmapContextCompatibilityKey: kCFBooleanTrue
        ] as CFDictionary

        var pixelBuffer: CVPixelBuffer?
        let status = CVPixelBufferCreate(
            kCFAllocatorDefault,
            Int(self.size.width),
            Int(self.size.height),
            kCVPixelFormatType_32ARGB,
            attrs,
            &pixelBuffer
        )

        guard status == kCVReturnSuccess else { return nil }

        CVPixelBufferLockBaseAddress(pixelBuffer!, CVPixelBufferLockFlags(rawValue: 0))
        defer {
            CVPixelBufferUnlockBaseAddress(pixelBuffer!, CVPixelBufferLockFlags(rawValue: 0))
        }

        let pixelData = CVPixelBufferGetBaseAddress(pixelBuffer!)
        let rgbColorSpace = CGColorSpaceCreateDeviceRGB()
        let context = CGContext(
            data: pixelData,
            width: Int(self.size.width),
            height: Int(self.size.height),
            bitsPerComponent: 8,
            bytesPerRow: CVPixelBufferGetBytesPerRow(pixelBuffer!),
            space: rgbColorSpace,
            bitmapInfo: CGImageAlphaInfo.noneSkipFirst.rawValue
        )

        context?.draw(self.cgImage!, in: CGRect(origin: .zero, size: self.size))

        return pixelBuffer
    }
}
```

### VNCoreMLRequest for Vision Integration

Use Vision framework with Core ML for advanced image processing:

```swift
import Vision
import CoreML

func detectObjectsWithVision(_ image: UIImage) {
    guard let cgImage = image.cgImage else { return }

    do {
        // Load Core ML model
        let model = try VNCoreMLModel(for: YOLOv8(configuration: MLModelConfiguration()).model)

        // Create request
        let request = VNCoreMLRequest(model: model) { request, error in
            if let results = request.results as? [VNRecognizedObjectObservation] {
                for observation in results {
                    if let topLabel = observation.labels.first {
                        print("Detected: \(topLabel.identifier) - Confidence: \(topLabel.confidence)")
                        print("Bounding box: \(observation.boundingBox)")
                    }
                }
            }
        }

        // Process image
        let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
        try handler.perform([request])

    } catch {
        print("Vision request error: \(error)")
    }
}
```

### Create ML for Model Training

Train models directly in Xcode using Create ML:

```swift
import CreateML

// Example of programmatic training (typically done in Xcode UI)
// For image classification:
// 1. Organize training data in folders: /data/class1/, /data/class2/
// 2. Use Create ML app or Swift for Training
// 3. Configure model parameters
// 4. Export as .mlmodel file

// Using trained model for predictions
func trainAndExportImageClassifier() {
    // This typically uses Create ML GUI, but can be scripted with MLModel
    let configuration = MLModelConfiguration()
    configuration.computeUnits = .cpuAndNeuralEngine

    // Load exported model
    guard let model = try? MobileNetV2(configuration: configuration) else {
        return
    }

    // Use model for inference
}
```

### Model Conversion (TensorFlow to Core ML)

```python
# Convert TensorFlow model to Core ML
import coremltools
import tensorflow as tf

# Load TensorFlow model
tf_model = tf.keras.models.load_model('model.h5')

# Convert to Core ML
core_ml_model = coremltools.convert(
    tf_model,
    source='tensorflow',
    inputs=[coremltools.ImageType(name='image', shape=(1, 224, 224, 3))],
    outputs=[coremltools.ClassifierOutputType(name='classLabel')]
)

# Set model metadata
core_ml_model.author = 'Your App'
core_ml_model.short_description = 'Image classifier'
core_ml_model.input_description['image'] = 'Input image'
core_ml_model.output_description['classLabel'] = 'Classification result'

# Save as .mlmodel
core_ml_model.save('ImageClassifier.mlmodel')
```

---

## 2. ML Kit (Google)

### Face Detection

```kotlin
// Android with ML Kit
import com.google.mlkit.vision.common.InputImage
import com.google.mlkit.vision.face.FaceDetection
import com.google.mlkit.vision.face.FaceDetectorOptions

fun detectFaces(bitmap: Bitmap) {
    val image = InputImage.fromBitmap(bitmap)

    val options = FaceDetectorOptions.Builder()
        .setPerformanceMode(FaceDetectorOptions.PERFORMANCE_MODE_ACCURATE)
        .setLandmarkMode(FaceDetectorOptions.LANDMARK_MODE_ALL)
        .setClassificationMode(FaceDetectorOptions.CLASSIFICATION_MODE_ALL)
        .build()

    val detector = FaceDetection.getClient(options)

    detector.process(image)
        .addOnSuccessListener { faces ->
            for (face in faces) {
                println("Face bounds: ${face.boundingBox}")
                println("Smiling: ${face.smilingProbability}")
                println("Eyes open: L=${face.leftEyeOpenProbability}, R=${face.rightEyeOpenProbability}")

                for (landmark in face.landmarks) {
                    println("Landmark ${landmark.landmarkType}: ${landmark.position}")
                }
            }
        }
        .addOnFailureListener { e ->
            println("Face detection failed: $e")
        }
}
```

### Text Recognition (OCR)

```swift
// iOS with ML Kit
import MLKitVision
import MLKitTextRecognition

func recognizeText(in image: UIImage) {
    let visionImage = VisionImage(image: image)

    let textRecognizer = TextRecognizer.textRecognizer()

    textRecognizer.process(visionImage) { result, error in
        guard let result = result, error == nil else {
            print("Text recognition error: \(error?.localizedDescription ?? "Unknown")")
            return
        }

        let fullText = result.text
        print("Full text: \(fullText)")

        for block in result.blocks {
            for line in block.lines {
                print("Line: \(line.text)")

                for element in line.elements {
                    print("Element: \(element.text)")
                    print("Confidence: \(element.confidence)")
                    print("Frame: \(element.frame)")
                }
            }
        }
    }
}
```

### Barcode Scanning

```kotlin
// Android with ML Kit
import com.google.mlkit.vision.barcode.BarcodeScanning
import com.google.mlkit.vision.barcode.Barcode

fun scanBarcodes(bitmap: Bitmap) {
    val image = InputImage.fromBitmap(bitmap)

    BarcodeScanning.getClient()
        .process(image)
        .addOnSuccessListener { barcodes ->
            for (barcode in barcodes) {
                val rawValue = barcode.rawValue
                val valueType = barcode.valueType

                when(valueType) {
                    Barcode.TYPE_URL -> {
                        val url = barcode.url
                        println("URL: ${url?.url}")
                    }
                    Barcode.TYPE_EMAIL -> {
                        val email = barcode.email
                        println("Email: ${email?.address}")
                    }
                    Barcode.TYPE_PHONE -> {
                        val phone = barcode.phone
                        println("Phone: ${phone?.number}")
                    }
                }
            }
        }
}
```

### Pose Detection

```swift
// iOS with ML Kit
import MLKitVision
import MLKitPoseDetection

func detectPose(in image: UIImage) {
    let visionImage = VisionImage(image: image)

    let options = PoseDetectorOptions()
    options.detectionMode = .singleImage

    let poseDetector = PoseDetector.poseDetector(options: options)

    poseDetector.process(visionImage) { pose, error in
        guard let pose = pose, error == nil else { return }

        for landmark in pose.landmarks {
            let position = landmark.position
            let type = landmark.type
            let z = landmark.z
            let inFrameLikelihood = landmark.inFrameLikelihood

            print("Landmark \(type): (\(position.x), \(position.y)) Z:\(z) Confidence:\(inFrameLikelihood)")
        }
    }
}
```

---

## 3. TensorFlow Lite

### Model Deployment and Interpreter

```kotlin
// Android with TensorFlow Lite
import org.tensorflow.lite.Interpreter
import org.tensorflow.lite.support.common.FileUtil
import org.tensorflow.lite.support.common.ops.NormalizeOp
import org.tensorflow.lite.support.image.ImageProcessor
import org.tensorflow.lite.support.image.TensorImage
import org.tensorflow.lite.support.image.ops.ResizeOp

class TFLiteClassifier(context: Context) {
    private lateinit var interpreter: Interpreter

    init {
        // Load model from assets
        val modelBuffer = FileUtil.loadMappedFile(context, "model.tflite")
        interpreter = Interpreter(modelBuffer)
    }

    fun classify(bitmap: Bitmap): ClassificationResult {
        // Preprocess image
        val imageProcessor = ImageProcessor.Builder()
            .add(ResizeOp(224, 224, ResizeOp.ResizeMethod.BILINEAR))
            .add(NormalizeOp(127.5f, 127.5f))
            .build()

        var tensorImage = TensorImage()
        tensorImage.load(bitmap)
        tensorImage = imageProcessor.process(tensorImage)

        // Run inference
        val outputArray = Array(1) { FloatArray(1000) }
        interpreter.run(tensorImage.buffer, outputArray)

        // Find max probability
        val results = outputArray[0]
        val maxIndex = results.indices.maxByOrNull { results[it] } ?: 0
        val confidence = results[maxIndex]

        return ClassificationResult(
            label = LABELS[maxIndex],
            confidence = confidence
        )
    }

    fun close() {
        interpreter.close()
    }
}

data class ClassificationResult(
    val label: String,
    val confidence: Float
)
```

### TensorFlow Lite on iOS

```swift
import TensorFlowLite

class TFLiteInterpreter {
    var interpreter: Interpreter?

    init(modelName: String) {
        let modelPath = Bundle.main.path(forResource: modelName, ofType: "tflite")!
        do {
            interpreter = try Interpreter(modelPath: modelPath)
            try interpreter?.allocateTensors()
        } catch {
            print("Failed to load model: \(error)")
        }
    }

    func predict(input: [[Float]]) -> [Float]? {
        guard let interpreter = interpreter else { return nil }

        do {
            let inputTensor = try interpreter.input(at: 0)
            let inputData = Data(copyingBufferOf: input.flatMap { $0 })

            try interpreter.copy(inputData, toInputAt: 0)
            try interpreter.invoke()

            let outputTensor = try interpreter.output(at: 0)
            let results = [Float](unsafeData: outputTensor.data) ?? []

            return results
        } catch {
            print("Prediction error: \(error)")
            return nil
        }
    }
}
```

### Quantization for TensorFlow Lite

```python
import tensorflow as tf

def quantize_model(model_path: str, output_path: str):
    """Convert model to quantized TFLite format"""

    # Load model
    model = tf.keras.models.load_model(model_path)

    # Create converter
    converter = tf.lite.TFLiteConverter.from_keras_model(model)

    # Enable quantization
    converter.target_spec.supported_ops = [
        tf.lite.OpsSet.TFLITE_BUILTINS_INT8
    ]
    converter.inference_input_type = tf.uint8
    converter.inference_output_type = tf.uint8

    # Dynamic range quantization (simpler)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]

    # Convert
    quantized_model = converter.convert()

    # Save
    with open(output_path, 'wb') as f:
        f.write(quantized_model)

    print(f"Quantized model saved to {output_path}")

# Full integer quantization with calibration
def quantize_with_calibration(model_path: str, calibration_data, output_path: str):
    """Full integer quantization with representative dataset"""

    converter = tf.lite.TFLiteConverter.from_keras_model(
        tf.keras.models.load_model(model_path)
    )

    def representative_dataset():
        for data in calibration_data:
            yield [tf.cast(data, tf.float32)]

    converter.representative_dataset = representative_dataset
    converter.target_spec.supported_ops = [
        tf.lite.OpsSet.TFLITE_BUILTINS_INT8
    ]

    quantized_model = converter.convert()

    with open(output_path, 'wb') as f:
        f.write(quantized_model)
```

---

## 4. On-Device LLMs

### Apple Intelligence (iOS 18+)

```swift
import NaturalLanguage

@available(iOS 18, *)
func generateTextWithAppleIntelligence() {
    let writeAssistant = WriteAssistantScheme()

    // Generate writing suggestions
    let text = "The user wants to write an email..."

    Task {
        do {
            let suggestions = try await writeAssistant.generateSuggestions(
                for: text,
                context: "professional email"
            )

            for suggestion in suggestions {
                print("Suggestion: \(suggestion.text)")
            }
        } catch {
            print("Error: \(error)")
        }
    }
}

@available(iOS 18, *)
func summarizeTextWithIntelligence(_ text: String) {
    Task {
        do {
            let summary = try await NLSummarizer.summarize(text, count: 2)
            print("Summary: \(summary)")
        } catch {
            print("Summarization error: \(error)")
        }
    }
}
```

### Gemini Nano (Android)

```kotlin
import com.google.ai.client.generativeai.GenerativeModel

class GeminiNanoChat {
    private val model = GenerativeModel(
        modelName = "gemini-nano",
        apiKey = "YOUR_API_KEY"
    )

    suspend fun chat(userMessage: String): String {
        return try {
            val response = model.generateContent(userMessage)
            response.text ?: "No response"
        } catch (e: Exception) {
            "Error: ${e.message}"
        }
    }

    suspend fun streamChat(userMessage: String) {
        model.generateContentStream(userMessage).collect { chunk ->
            print(chunk.text)
        }
    }
}
```

### llama.cpp Mobile (Cross-platform)

```swift
// iOS with llama.cpp
import Foundation

class LlamaModel {
    private var context: OpaquePointer?

    init(modelPath: String) {
        var params = llama_context_default_params()
        params.n_ctx = 512
        params.n_threads = 4

        context = llama_new_context_with_model(
            llama_load_model_from_file(modelPath, params),
            params
        )
    }

    func generateText(prompt: String, maxTokens: Int) -> String {
        guard let ctx = context else { return "" }

        var tokens = [llama_token](repeating: 0, count: 512)
        let numTokens = llama_tokenize(
            ctx,
            prompt,
            &tokens,
            512,
            true
        )

        var output = ""

        for _ in 0..<maxTokens {
            llama_eval(ctx, tokens, numTokens, 0, 4)

            let nextToken = llama_sample_top_p_top_k(ctx, .zero, 40, 0.9, 1.0, 1.0)

            let piece = llama_token_to_str(ctx, nextToken)
            output += String(cString: piece)
        }

        return output
    }

    deinit {
        if let ctx = context {
            llama_free(ctx)
        }
    }
}
```

---

## 5. Vision Tasks

### Image Classification

```swift
// Using Vision framework
import Vision
import CoreML

func classifyImage(_ ciImage: CIImage) {
    do {
        let model = try VNCoreMLModel(for: MobileNetV2(configuration: MLModelConfiguration()).model)

        let request = VNCoreMLRequest(model: model) { request, error in
            guard let results = request.results as? [VNClassificationObservation] else {
                return
            }

            for classification in results.prefix(5) {
                print("\(classification.identifier): \(classification.confidence)")
            }
        }

        let handler = VNImageRequestHandler(ciImage: ciImage)
        try handler.perform([request])
    } catch {
        print("Classification error: \(error)")
    }
}
```

### Object Detection (YOLO)

```kotlin
// Android with YOLO
import org.tensorflow.lite.Interpreter

class YOLODetector(context: Context) {
    private val interpreter: Interpreter
    private val inputSize = 416

    init {
        val modelBuffer = FileUtil.loadMappedFile(context, "yolov5.tflite")
        interpreter = Interpreter(modelBuffer)
    }

    fun detectObjects(bitmap: Bitmap): List<Detection> {
        val resized = Bitmap.createScaledBitmap(bitmap, inputSize, inputSize, true)
        val input = convertBitmapToByteBuffer(resized)

        val output = Array(1) { Array(25200) { FloatArray(85) } }
        interpreter.run(input, output)

        return parseYOLOOutput(output[0])
    }

    private fun parseYOLOOutput(output: Array<FloatArray>): List<Detection> {
        val detections = mutableListOf<Detection>()
        val confidenceThreshold = 0.5f

        for (i in output.indices) {
            val confidence = output[i][4]
            if (confidence > confidenceThreshold) {
                val classId = output[i].slice(5..84).withIndex()
                    .maxByOrNull { it.value }?.index ?: 0

                detections.add(
                    Detection(
                        x = output[i][0],
                        y = output[i][1],
                        width = output[i][2],
                        height = output[i][3],
                        confidence = confidence,
                        classId = classId,
                        className = COCO_CLASSES[classId]
                    )
                )
            }
        }

        return suppressNonMaxima(detections)
    }

    private fun suppressNonMaxima(detections: List<Detection>): List<Detection> {
        val sorted = detections.sortedByDescending { it.confidence }
        val result = mutableListOf<Detection>()

        for (detection in sorted) {
            var overlaps = false
            for (kept in result) {
                if (iouScore(detection, kept) > 0.5f) {
                    overlaps = true
                    break
                }
            }
            if (!overlaps) result.add(detection)
        }

        return result
    }
}

data class Detection(
    val x: Float,
    val y: Float,
    val width: Float,
    val height: Float,
    val confidence: Float,
    val classId: Int,
    val className: String
)
```

### OCR (Optical Character Recognition)

```python
# Using pytesseract for reference (mobile uses native frameworks)
import pytesseract
from PIL import Image

def extract_text(image_path: str) -> str:
    """Extract text from image using OCR"""
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text

def extract_with_confidence(image_path: str):
    """Get OCR results with confidence scores"""
    image = Image.open(image_path)
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

    results = []
    for i in range(len(data['text'])):
        if int(data['conf'][i]) > 30:  # Filter by confidence
            results.append({
                'text': data['text'][i],
                'confidence': int(data['conf'][i]),
                'bbox': (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
            })

    return results
```

---

## 6. Natural Language Processing

### Text Classification

```swift
import NaturalLanguage

func classifyText(_ text: String) {
    let tagger = NLTagger(tagSchemes: [.sentimentScore])
    tagger.string = text

    let (sentiment, _) = tagger.tag(
        at: text.startIndex,
        unit: .paragraph,
        scheme: .sentimentScore
    )

    if let sentiment = sentiment {
        let score = Double(sentiment.rawValue) ?? 0
        print("Sentiment: \(score)")  // -1 to 1, -1=negative, 1=positive
    }
}

// Custom text classifier with Core ML
class TextClassifier {
    let model: TextClassificationModel

    func classify(_ text: String) -> String? {
        do {
            let featureProvider = try DictVectorizer.convert(text)
            let output = try model.prediction(input: featureProvider as! TextClassificationModelInput)
            return output.label
        } catch {
            print("Classification error: \(error)")
            return nil
        }
    }
}
```

### Sentiment Analysis

```kotlin
// Android with TensorFlow Lite
class SentimentAnalyzer(context: Context) {
    private val interpreter: Interpreter
    private val vocabulary: Map<String, Int>

    init {
        val modelBuffer = FileUtil.loadMappedFile(context, "sentiment_model.tflite")
        interpreter = Interpreter(modelBuffer)
        vocabulary = loadVocabulary(context)
    }

    fun analyzeSentiment(text: String): SentimentScore {
        val tokens = text.lowercase().split(" ")
        val indices = tokens.map { vocabulary[it] ?: 0 }.toIntArray()

        // Pad or truncate to fixed length
        val input = IntArray(128)
        indices.copyInto(input, 0, 0, minOf(indices.size, 128))

        val output = Array(1) { FloatArray(3) }
        interpreter.run(input, output)

        val scores = output[0]
        return SentimentScore(
            negative = scores[0],
            neutral = scores[1],
            positive = scores[2]
        )
    }
}

data class SentimentScore(
    val negative: Float,
    val neutral: Float,
    val positive: Float
)
```

### Named Entity Extraction

```swift
import NaturalLanguage

func extractEntities(_ text: String) {
    let tagger = NLTagger(tagSchemes: [.nameType])
    tagger.string = text

    let options: NLTagger.Options = [.omitPunctuation, .omitWhitespace]

    tagger.enumerateTags(in: text.startIndex..<text.endIndex, unit: .word, scheme: .nameType, options: options) { tag, tokenRange in
        if let tag = tag {
            let entity = String(text[tokenRange])
            print("Entity: \(entity) - Type: \(tag.rawValue)")
        }
        return true
    }
}

// Entity types: person, place, organization, personalName, placeName, organizationName
```

### Machine Translation

```kotlin
// Android with TensorFlow Lite for translation
class TranslationModel(context: Context) {
    private val encoder: Interpreter
    private val decoder: Interpreter

    fun translate(text: String, sourceLanguage: String, targetLanguage: String): String {
        // Tokenize input
        val tokens = tokenize(text)

        // Encode
        val encoderOutput = runEncoder(tokens)

        // Decode with attention
        var decodedTokens = mutableListOf<Int>()
        var currentInput = intArrayOf(1) // Start token

        for (step in 0 until MAX_DECODE_LENGTH) {
            val decoderOutput = runDecoder(currentInput, encoderOutput)
            val nextToken = decoderOutput.argMax()

            if (nextToken == 2) break // End token

            decodedTokens.add(nextToken)
            currentInput = intArrayOf(nextToken)
        }

        return detokenize(decodedTokens)
    }
}
```

---

## 7. Speech Recognition and Synthesis

### Speech-to-Text (iOS)

```swift
import Speech
import AVFoundation

class SpeechRecognizer: NSObject, SFSpeechRecognizerDelegate {
    let speechRecognizer = SFSpeechRecognizer(locale: Locale(identifier: "en-US"))
    let audioEngine = AVAudioEngine()
    var recognitionRequest: SFSpeechAudioBufferRecognitionRequest?
    var recognitionTask: SFSpeechRecognitionTask?

    func startRecording() throws {
        // Cancel previous task if running
        recognitionTask?.cancel()
        recognitionTask = nil

        // Configure audio session
        let audioSession = AVAudioSession.sharedInstance()
        try audioSession.setCategory(.record, mode: .measurement, options: .duckOthers)
        try audioSession.setActive(true, options: .notifyOthersOnDeactivation)

        recognitionRequest = SFSpeechAudioBufferRecognitionRequest()
        guard let recognitionRequest = recognitionRequest else { return }

        recognitionRequest.shouldReportPartialResults = true
        recognitionRequest.requiresOnDeviceRecognition = true

        // Create recognition task
        recognitionTask = speechRecognizer?.recognitionTask(with: recognitionRequest) { result, error in
            if let result = result {
                let isFinal = result.isFinal
                print("Recognized: \(result.bestTranscription.formattedString)")
                print("Is Final: \(isFinal)")

                if isFinal {
                    self.stopRecording()
                }
            }

            if let error = error {
                print("Speech recognition error: \(error)")
            }
        }

        // Set up audio input
        let inputNode = audioEngine.inputNode
        let recordingFormat = inputNode.outputFormat(forBus: 0)!
        inputNode.installTap(onBus: 0, bufferSize: 1024, format: recordingFormat) { buffer, _ in
            recognitionRequest.append(buffer)
        }

        audioEngine.prepare()
        try audioEngine.start()
    }

    func stopRecording() {
        audioEngine.stop()
        audioEngine.inputNode.removeTap(onBus: 0)
        recognitionRequest?.endAudio()
        recognitionTask?.cancel()
    }
}
```

### Speech-to-Text (Android)

```kotlin
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer

class AndroidSpeechRecognizer(context: Context) {
    private val speechRecognizer = SpeechRecognizer.createSpeechRecognizer(context)

    fun startListening(onResult: (String) -> Unit) {
        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, "en-US")
            putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, true)
            putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1)
        }

        speechRecognizer.setRecognitionListener(object : RecognitionListener {
            override fun onResults(results: Bundle?) {
                val matches = results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                if (!matches.isNullOrEmpty()) {
                    onResult(matches[0])
                }
            }

            override fun onPartialResults(partialResults: Bundle?) {
                val partial = partialResults?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                if (!partial.isNullOrEmpty()) {
                    onResult(partial[0])
                }
            }

            override fun onError(error: Int) {
                println("Speech recognition error: $error")
            }

            override fun onReadyForSpeech(params: Bundle?) {}
            override fun onBeginningOfSpeech() {}
            override fun onRmsChanged(rmsdB: Float) {}
            override fun onBufferReceived(buffer: ByteArray?) {}
            override fun onEndOfSpeech() {}
        })

        speechRecognizer.startListening(intent)
    }
}
```

### Text-to-Speech

```swift
import AVFoundation

class TextToSpeech {
    let synthesizer = AVSpeechSynthesizer()

    func speak(_ text: String, language: String = "en-US") {
        let utterance = AVSpeechUtterance(string: text)
        utterance.voice = AVSpeechSynthesisVoice(language: language)
        utterance.rate = AVSpeechUtteranceDefaultSpeechRate
        utterance.pitchMultiplier = 1.0
        utterance.volume = 0.8

        synthesizer.speak(utterance)
    }

    func stop() {
        synthesizer.stopSpeaking(at: .immediate)
    }
}

// Android equivalent
class AndroidTextToSpeech(context: Context) {
    private val tts = TextToSpeech(context) { status ->
        if (status == TextToSpeech.SUCCESS) {
            tts.language = Locale.US
        }
    }

    fun speak(text: String) {
        tts.speak(text, TextToSpeech.QUEUE_FLUSH, null)
    }
}
```

---

## 8. Model Optimization

### Quantization

```python
# Post-training quantization
import torch
from torch.quantization import quantize_dynamic

model = torch.jit.script(your_model)
quantized_model = quantize_dynamic(
    model,
    {torch.nn.Linear},
    dtype=torch.qint8
)
torch.jit.save(quantized_model, 'quantized_model.pt')
```

### Pruning

```python
import torch
from torch.nn.utils import prune

# Structured pruning (remove entire channels)
for name, module in model.named_modules():
    if isinstance(module, torch.nn.Linear):
        prune.ln_structured(module, name='weight', amount=0.3, n=2, dim=0)

# Unstructured pruning (remove individual weights)
prune.l1_unstructured(model.conv1, name='weight', amount=0.2)

# Make pruning permanent
for module in model.modules():
    if isinstance(module, torch.nn.modules.utils.parametrized_module):
        prune.remove(module, 'weight')

torch.save(model.state_dict(), 'pruned_model.pt')
```

### Knowledge Distillation

```python
import torch
import torch.nn as nn

class DistillationLoss(nn.Module):
    def __init__(self, temperature=4.0, alpha=0.5):
        super().__init__()
        self.temperature = temperature
        self.alpha = alpha
        self.kl_loss = nn.KLDivLoss(reduction='batchmean')
        self.ce_loss = nn.CrossEntropyLoss()

    def forward(self, student_logits, teacher_logits, labels):
        # Teacher predictions (no gradients)
        with torch.no_grad():
            teacher_probs = torch.softmax(teacher_logits / self.temperature, dim=1)

        # Student predictions
        student_log_probs = torch.log_softmax(student_logits / self.temperature, dim=1)

        # KL divergence loss
        kl_loss = self.kl_loss(student_log_probs, teacher_probs)

        # Cross-entropy loss with true labels
        ce_loss = self.ce_loss(student_logits, labels)

        # Combined loss
        total_loss = self.alpha * kl_loss + (1 - self.alpha) * ce_loss
        return total_loss

# Training loop
def train_student(student, teacher, train_loader, epochs=10):
    optimizer = torch.optim.Adam(student.parameters(), lr=0.001)
    distillation_loss = DistillationLoss(temperature=4.0, alpha=0.7)

    for epoch in range(epochs):
        for images, labels in train_loader:
            teacher_logits = teacher(images)
            student_logits = student(images)

            loss = distillation_loss(student_logits, teacher_logits, labels)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
```

---

## 9. Federated Learning Concepts

```swift
// Federated learning simulation on mobile
class FederatedLearningClient {
    var localModel: MLModel
    let modelUpdates = ModelUpdateBuffer()

    func performLocalTraining(on data: [TrainingData]) {
        // Train on local device data only
        var loss: Float = 0.0
        for batch in data.chunked(into: 32) {
            loss = localModel.train(on: batch)
        }
    }

    func aggregateGlobalModel(with globalModel: MLModel) {
        // Federated Averaging (FedAvg)
        // Only send weight updates, not raw data
        let weights = extractWeights(from: localModel)
        let globalWeights = extractWeights(from: globalModel)

        let delta = weights.map { $0 - globalWeights[$0.index] }
        modelUpdates.addUpdate(delta)

        // Send encrypted update to server (not raw data!)
        sendEncryptedUpdate(delta)
    }
}

// Privacy-preserving aggregation
class FederatedAggregator {
    func aggregateUpdates(_ clientUpdates: [[Float]]) -> [Float] {
        let clientCount = Float(clientUpdates.count)

        guard let firstUpdate = clientUpdates.first else {
            return []
        }

        var aggregated = Array(repeating: 0.0, count: firstUpdate.count)

        for update in clientUpdates {
            for (index, value) in update.enumerated() {
                aggregated[index] += value / clientCount
            }
        }

        return aggregated
    }

    // Differential privacy: add noise
    func addDifferentialPrivacy(
        _ aggregated: [Float],
        epsilon: Float = 1.0,
        delta: Float = 1e-5
    ) -> [Float] {
        return aggregated.map { value in
            let noise = Float.random(in: -1...1) * (1.0 / epsilon)
            return value + noise
        }
    }
}
```

---

## 10. Predictive UX

### Intelligent Pre-fetching

```swift
import Network

class PredictivePreFetcher {
    let monitor = NWPathMonitor()
    var predictions: [String] = []

    func predictNextContent(basedOn userBehavior: [UserAction]) -> [String] {
        // Analyze pattern
        let lastActions = userBehavior.suffix(5)

        // Simple Markov chain prediction
        let transitions = buildTransitionMatrix(from: userBehavior)
        let currentState = userBehavior.last?.content ?? "home"

        var predicted: [String] = []
        var state = currentState

        for _ in 0..<3 {
            let nextState = transitions[state]?.max()?.key ?? "unknown"
            predicted.append(nextState)
            state = nextState
        }

        return predicted
    }

    func prefetchPredictedContent(_ urls: [URL]) {
        monitor.pathUpdateHandler = { path in
            if path.status == .satisfied {
                for url in urls {
                    URLSession.shared.dataTask(with: url).resume()
                }
            }
        }
    }
}
```

### Smart Suggestions

```kotlin
// Android with ML Kit
class SmartSuggestions(private val context: Context) {
    private val model: RecommendationModel

    fun suggestNextAction(userHistory: List<UserAction>): List<Suggestion> {
        // Extract features from history
        val features = featureExtractor.extract(userHistory)

        // Run inference
        val predictions = model.predict(features)

        // Convert to ranked suggestions
        return predictions
            .mapIndexed { index, score ->
                Suggestion(
                    action = ACTIONS[index],
                    confidence = score,
                    reason = generateReason(index, score)
                )
            }
            .sortedByDescending { it.confidence }
    }

    fun optimizeUILayout(suggestions: List<Suggestion>) {
        // Reorder UI elements based on predictions
        // Place most likely actions in prominent positions
    }
}
```

---

## 11. Health & Fitness ML

### Activity Recognition

```swift
import CoreMotion

class ActivityRecognizer {
    let motionManager = CMMotionManager()
    let classifier: MLModel
    var accelerometerData: [(x: Double, y: Double, z: Double)] = []

    func startActivityRecognition() {
        motionManager.accelerometerUpdateInterval = 0.1
        motionManager.startAccelerometerUpdates(to: .main) { data, error in
            guard let data = data else { return }

            self.accelerometerData.append((
                data.acceleration.x,
                data.acceleration.y,
                data.acceleration.z
            ))

            // Classify every 100 samples (10 seconds at 0.1s intervals)
            if self.accelerometerData.count >= 100 {
                self.classifyActivity()
                self.accelerometerData.removeFirst(50) // Sliding window
            }
        }
    }

    func classifyActivity() {
        let features = extractFeatures(from: accelerometerData)

        do {
            let input = ActivityInput(
                mean_x: features.meanX,
                mean_y: features.meanY,
                mean_z: features.meanZ,
                std_x: features.stdX,
                std_y: features.stdY,
                std_z: features.stdZ
            )

            let output = try classifier.prediction(input: input)
            print("Activity: \(output.activity)")
        } catch {
            print("Classification error: \(error)")
        }
    }

    func extractFeatures(from data: [(x: Double, y: Double, z: Double)]) -> Features {
        let xs = data.map { $0.x }
        let ys = data.map { $0.y }
        let zs = data.map { $0.z }

        return Features(
            meanX: xs.reduce(0, +) / Double(xs.count),
            meanY: ys.reduce(0, +) / Double(ys.count),
            meanZ: zs.reduce(0, +) / Double(zs.count),
            stdX: calculateStd(xs),
            stdY: calculateStd(ys),
            stdZ: calculateStd(zs)
        )
    }
}

struct Features {
    let meanX, meanY, meanZ: Double
    let stdX, stdY, stdZ: Double
}
```

### Heart Rate Analysis

```kotlin
// Android with Health Connect API
class HeartRateAnalyzer(private val context: Context) {
    private val healthConnectClient = HealthConnectClient.getOrCreate(context)

    suspend fun analyzeHeartRate(): HeartRateMetrics {
        val records = healthConnectClient.readRecords(
            ReadRecordsRequest(
                recordType = HeartRateRecord::class,
                timeRangeFilter = TimeRangeFilter.between(
                    startTime = Instant.now().minus(Duration.ofDays(7)),
                    endTime = Instant.now()
                )
            )
        )

        val heartRates = (records as ReadRecordsResponse<HeartRateRecord>)
            .records
            .map { it.samples.first().beatsPerMinute }

        return HeartRateMetrics(
            average = heartRates.average(),
            min = heartRates.minOrNull() ?: 0,
            max = heartRates.maxOrNull() ?: 0,
            heartRateVariability = calculateHRV(heartRates),
            restingHeartRate = estimateRestingHR(heartRates),
            cardioFitness = estimateVO2Max(heartRates)
        )
    }

    private fun calculateHRV(heartRates: List<Double>): Double {
        // Heart Rate Variability: standard deviation of RR intervals
        val intervals = heartRates.zipWithNext { a, b -> b - a }
        return sqrt(intervals.map { (it - intervals.average()).pow(2) }.average())
    }

    private fun estimateRestingHR(heartRates: List<Double>): Double {
        // Lowest recorded heart rate (typically during sleep/rest)
        return heartRates.minOrNull() ?: 0.0
    }

    private fun estimateVO2Max(heartRates: List<Double>): Double {
        // Simplified VO2 Max estimation (normally requires exercise data)
        val restingHR = estimateRestingHR(heartRates)
        return 15.3 * (220 - 30) / restingHR
    }
}

data class HeartRateMetrics(
    val average: Double,
    val min: Int,
    val max: Int,
    val heartRateVariability: Double,
    val restingHeartRate: Double,
    val cardioFitness: Double
)
```

---

## Best Practices & Performance Tips

### Model Selection
- Use smaller models (MobileNet, SqueezeNet) for on-device inference
- Prefer integer quantization for ~4x model size reduction
- Consider edge cases during testing

### Privacy & Security
- Keep training data local (federated learning approach)
- Encrypt model updates before transmission
- Validate model inputs to prevent adversarial attacks

### Performance Optimization
- Profile on target devices (real hardware matters)
- Use GPU delegates when available (Metal on iOS, GPU on Android)
- Implement async processing to avoid blocking UI

### Battery Efficiency
- Minimize ML operations on battery-constrained devices
- Use low-power modes for health monitoring
- Batch operations when possible

### Testing
- Unit test feature extraction pipelines
- Cross-validate model performance on multiple devices
- Monitor for model drift in production

