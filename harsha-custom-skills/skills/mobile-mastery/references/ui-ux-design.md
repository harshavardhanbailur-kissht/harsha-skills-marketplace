# Mobile UI/UX Design Reference

## Table of Contents

- [1. Apple HIG Essentials](#1-apple-hig-essentials)
- [2. Material Design 3](#2-material-design-3)
- [3. Responsive Design](#3-responsive-design)
- [4. Typography](#4-typography)
- [5. Color Systems](#5-color-systems)
- [6. Touch Targets](#6-touch-targets)
- [7. Navigation Patterns](#7-navigation-patterns)
- [8. Form Design](#8-form-design)
- [9. Loading States](#9-loading-states)
- [10. Empty & Error States](#10-empty--error-states)
- [11. Onboarding](#11-onboarding)
- [12. Design Tokens](#12-design-tokens)
- [13. Localization UX](#13-localization-ux)

---

## 1. Apple HIG Essentials

### Core Principles
- **Clarity**: Interface should help users understand what's possible and how to engage
- **Deference**: Content should take center stage
- **Depth**: Visual layers and realistic motion convey hierarchy and enable understanding

### iOS Design Patterns
- **Bars**: Status bars, navigation bars, tab bars, and toolbars
- **Views**: Modal presentations, popovers, page view controllers
- **Controls**: Buttons, segmented controls, switches, sliders
- **Search Interface**: Search bars and scope bars
- **Table & Collection Views**: Data presentation patterns

### SF Symbols
Consistent, scalable symbol system (over 6,000+ symbols):
```swift
// SwiftUI - SF Symbols usage
Image(systemName: "star.fill")
    .font(.system(size: 24, weight: .semibold))
    .foregroundColor(.yellow)

// Weighted variants
Image(systemName: "heart")
    .imageScale(.large)
    .symbolVariant(.fill)
    .foregroundColor(.red)

// Hierarchical rendering
Image(systemName: "bell.and.waves.left.and.right")
    .symbolRenderingMode(.hierarchical)
    .foregroundColor(.blue)
```

---

## 2. Material Design 3

### Design Tokens
Material Design 3 uses a token-based system:
```kotlin
// Jetpack Compose - Material 3 tokens
val typography = Typography(
    bodyLarge = TextStyle(
        fontFamily = FontFamily.Default,
        fontSize = 16.sp,
        lineHeight = 24.sp,
        letterSpacing = 0.5.sp
    ),
    headlineSmall = TextStyle(
        fontFamily = FontFamily.Default,
        fontSize = 24.sp,
        fontWeight = FontWeight.Bold
    )
)

val colorScheme = lightColorScheme(
    primary = Color(0xFF6750a4),
    secondary = Color(0xFF625b71),
    tertiary = Color(0xFF7d5260),
    surface = Color(0xFFFFFBFE)
)
```

### Dynamic Color
Adaptive color system based on device wallpaper (Android 12+):
```kotlin
// Material 3 Dynamic Color in Compose
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
    val dynamicColorScheme = dynamicLightColorScheme(context)
} else {
    val colorScheme = lightColorScheme(
        primary = Color(0xFF6750a4)
    )
}
```

### Component Guidelines
- Buttons: Filled, Outlined, Elevated, Text, Tonal variants
- Cards: Standard, Elevated, Outlined variants
- Text fields: Filled and Outlined styles
- Lists: Single-line, two-line, three-line with leading/trailing elements

---

## 3. Responsive Design

### Safe Areas
Accounting for notches, Dynamic Island, and system UI:
```swift
// SwiftUI safe area
VStack {
    Text("Header")
        .frame(maxWidth: .infinity)

    ScrollView {
        VStack(spacing: 16) {
            ForEach(0..<10, id: \.self) { i in
                Text("Item \(i)")
            }
        }
        .padding(.horizontal)
    }
}
.ignoresSafeArea(edges: [.top, .bottom])
.safeAreaInset(edge: .top) {
    Color.blue.frame(height: 44)
}
```

### Notches and Dynamic Island
```swift
// Dynamic Island adaptation
@Environment(\.verticalSizeClass) var vSizeClass
@Environment(\.horizontalSizeClass) var hSizeClass

VStack {
    if hSizeClass == .compact && vSizeClass == .regular {
        // iPhone portrait
        iPhonePortraitLayout()
    } else if hSizeClass == .regular {
        // iPad or landscape
        iPadLayout()
    }
}
```

### Adaptive Layouts
```kotlin
// Compose - Responsive layout
@Composable
fun ResponsiveLayout(windowSizeClass: WindowSizeClass) {
    when (windowSizeClass.widthSizeClass) {
        WindowWidthSizeClass.Compact -> {
            // Phone layout
            SingleColumnLayout()
        }
        WindowWidthSizeClass.Medium -> {
            // Tablet or landscape
            TwoColumnLayout()
        }
        WindowWidthSizeClass.Expanded -> {
            // Large tablet or foldable
            ThreeColumnLayout()
        }
    }
}
```

### Foldable Support
```kotlin
// Jetpack WindowManager for foldables
val windowMetrics = WindowMetricsCalculator.getOrCreate()
    .computeCurrentWindowMetrics(activity)
val bounds = windowMetrics.bounds

val foldingFeatures = WindowManager.getWindowLayoutComponent()
    ?.getAllFoldingFeatures(activity)

foldingFeatures?.forEach { fold ->
    when (fold.orientation) {
        FoldingFeature.Orientation.VERTICAL -> {
            // Handle vertical fold (hinge on left/right)
            val foldPosition = fold.bounds.left
        }
        FoldingFeature.Orientation.HORIZONTAL -> {
            // Handle horizontal fold (hinge on top/bottom)
            val foldPosition = fold.bounds.top
        }
    }
}
```

---

## 4. Typography

### iOS Type Scale
Apple uses a relative sizing system:
```swift
// SwiftUI Typography
VStack(spacing: 16) {
    Text("Large Title")
        .font(.largeTitle)  // 34pt, semibold

    Text("Title 1")
        .font(.title)       // 28pt, semibold

    Text("Headline")
        .font(.headline)    // 17pt, semibold

    Text("Body")
        .font(.body)        // 17pt, regular

    Text("Callout")
        .font(.callout)     // 16pt, regular

    Text("Subheadline")
        .font(.subheadline) // 15pt, regular

    Text("Caption 1")
        .font(.caption)     // 12pt, regular
}

// Custom typography
Text("Custom")
    .font(.system(size: 20, weight: .semibold, design: .default))
```

### Android Type Scale
Material Design 3 defines 5 typographic levels:
```kotlin
// Compose Typography
val typography = Typography(
    displayLarge = TextStyle(  // 57sp, weight 400, letter spacing 0sp
        fontSize = 57.sp,
        fontWeight = FontWeight.Normal
    ),
    headlineLarge = TextStyle(  // 32sp, weight 400
        fontSize = 32.sp
    ),
    bodyMedium = TextStyle(     // 14sp, weight 500
        fontSize = 14.sp,
        fontWeight = FontWeight.Medium
    )
)

Text(
    text = "Headline",
    style = MaterialTheme.typography.headlineSmall
)
```

### Dynamic Type (iOS)
Respects user accessibility settings:
```swift
// SwiftUI with dynamic type
@Environment(\.dynamicTypeSize) var dynamicTypeSize

VStack {
    Text("This text scales with user preferences")
        .font(.headline)
        .lineLimit(nil)  // Allow wrapping

    if dynamicTypeSize > .large {
        // Adjust layout for larger text
        VStack { /* Vertical layout */ }
    } else {
        HStack { /* Horizontal layout */ }
    }
}
```

### Custom Fonts
```swift
// SwiftUI custom font loading
extension Font {
    static func customFont(name: String, size: CGFloat) -> Font {
        return Font.custom(name, size: size)
    }
}

Text("Custom Font")
    .font(.customFont(name: "CustomFont-Bold", size: 18))

// iOS 17+
Text("Custom Font")
    .font(.system(size: 18, design: .default))
    .fontDesign(.rounded)
```

---

## 5. Color Systems

### Dark Mode Implementation
```swift
// SwiftUI color adaptation
struct AppColors {
    static let backgroundColor = Color(UIColor { traitCollection in
        traitCollection.userInterfaceStyle == .dark ?
            UIColor(red: 0.1, green: 0.1, blue: 0.1, alpha: 1) :
            UIColor.white
    })

    static let textColor = Color(UIColor { traitCollection in
        traitCollection.userInterfaceStyle == .dark ?
            UIColor.white :
            UIColor.black
    })
}

// SwiftUI environment override
.preferredColorScheme(.dark)  // Force dark mode
.preferredColorScheme(nil)    // Follow system
```

### Kotlin/Compose Dark Mode
```kotlin
// Dynamic color scheme based on Android API
@Composable
fun AppTheme(
    isDarkMode: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val colorScheme = if (isDarkMode) {
        darkColorScheme(
            primary = Color(0xFFB3E5FC),
            surface = Color(0xFF121212)
        )
    } else {
        lightColorScheme(
            primary = Color(0xFF0288D1),
            surface = Color(0xFFFFFFFF)
        )
    }

    MaterialTheme(
        colorScheme = colorScheme,
        content = content
    )
}
```

### Accessibility: WCAG 4.5:1 Contrast
```swift
// Color contrast validation
struct ColorContrast {
    static func contrastRatio(light: UIColor, dark: UIColor) -> Double {
        let lightLuminance = light.relativeLight()
        let darkLuminance = dark.relativeLight()
        let lighter = max(lightLuminance, darkLuminance)
        let darker = min(lightLuminance, darkLuminance)
        return (lighter + 0.05) / (darker + 0.05)
    }
}

// Semantic colors for consistency
struct SemanticColors {
    static let successBackground = Color(UIColor { traitCollection in
        traitCollection.userInterfaceStyle == .dark ?
            UIColor(red: 0.2, green: 0.4, blue: 0.3, alpha: 0.1) :
            UIColor(red: 0.7, green: 1.0, blue: 0.8, alpha: 0.2)
    })
}
```

---

## 6. Touch Targets

### iOS Minimum Touch Target (44pt)
```swift
// SwiftUI - minimum 44pt tap area
Button(action: { }) {
    Text("Tap Me")
}
.frame(minHeight: 44)  // Minimum height
.padding(.horizontal, 16)

// Larger touch target with invisible area
Button(action: { }) {
    Image(systemName: "plus")
}
.frame(width: 44, height: 44)  // 44pt square
.contentShape(Rectangle())  // Expand hitbox

// Spacing between touch targets
VStack(spacing: 8) {
    ForEach(items, id: \.self) { item in
        Button(item.title) { }
            .frame(minHeight: 44)
    }
}
```

### Android Minimum Touch Target (48dp)
```kotlin
// Compose - 48dp minimum touch target
Button(
    onClick = { },
    modifier = Modifier
        .height(48.dp)  // Material Design minimum
        .padding(horizontal = 16.dp)
) {
    Text("Tap Me")
}

// Semantic touch area
IconButton(
    onClick = { },
    modifier = Modifier
        .size(48.dp)  // 48x48dp
        .padding(8.dp)
) {
    Icon(Icons.Default.Add, contentDescription = null)
}
```

### Gesture Zones
```swift
// SwiftUI gesture handling
VStack {
    // Thumb zone (bottom 2/3 of screen)
    Text("Easy to tap")
        .gesture(
            TapGesture()
                .onEnded { /* Thumb zone action */ }
        )

    // Hard to reach (top corners)
    Text("Difficult area")
}

// Gesture priority
ZStack {
    Color.blue
        .gesture(TapGesture().onEnded { /* Parent */ })

    Button("Inner") { /* Child takes priority */ }
}
```

---

## 7. Navigation Patterns

### Tab Bar Navigation (iOS)
```swift
// SwiftUI TabView
@main
struct AppView: View {
    @State var selectedTab = 0

    var body: some View {
        TabView(selection: $selectedTab) {
            HomeView()
                .tabItem {
                    Label("Home", systemImage: "house")
                }
                .tag(0)

            SearchView()
                .tabItem {
                    Label("Search", systemImage: "magnifyingglass")
                }
                .tag(1)

            ProfileView()
                .tabItem {
                    Label("Profile", systemImage: "person")
                }
                .tag(2)
        }
    }
}
```

### Navigation Drawer (Android)
```kotlin
// Compose NavigationDrawer
val drawerState = rememberDrawerState(DrawerValue.Closed)
val scope = rememberCoroutineScope()

ModalNavigationDrawer(
    drawerContent = {
        ModalDrawerSheet {
            NavigationDrawerItem(
                label = { Text("Home") },
                selected = selectedItem == "home",
                onClick = {
                    selectedItem = "home"
                    scope.launch { drawerState.close() }
                },
                modifier = Modifier.padding(horizontal = 12.dp)
            )
            NavigationDrawerItem(
                label = { Text("Settings") },
                selected = selectedItem == "settings",
                onClick = {
                    selectedItem = "settings"
                    scope.launch { drawerState.close() }
                }
            )
        }
    },
    drawerState = drawerState
) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("App Title") },
                navigationIcon = {
                    IconButton(
                        onClick = { scope.launch { drawerState.open() } }
                    ) {
                        Icon(Icons.Default.Menu, "Menu")
                    }
                }
            )
        }
    ) { paddingValues ->
        MainContent(Modifier.padding(paddingValues))
    }
}
```

### Bottom Sheet
```swift
// SwiftUI bottom sheet
.sheet(isPresented: $showSheet) {
    VStack(spacing: 16) {
        Text("Sheet Title")
            .font(.headline)

        Text("Content goes here")

        Button("Close") {
            showSheet = false
        }
    }
    .presentationDetents([.medium, .large])
    .presentationDragIndicator(.visible)
}
```

```kotlin
// Compose BottomSheet
val bottomSheetScaffoldState = rememberBottomSheetScaffoldState()
val scope = rememberCoroutineScope()

BottomSheetScaffold(
    scaffoldState = bottomSheetScaffoldState,
    sheetContent = {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            Text("Sheet Title", style = MaterialTheme.typography.headlineSmall)
            Text("Content here")
        }
    },
    sheetPeekHeight = 128.dp
) {
    Button(onClick = {
        scope.launch { bottomSheetScaffoldState.bottomSheetState.expand() }
    }) {
        Text("Show Sheet")
    }
}
```

### Modal / Dialog
```swift
// SwiftUI modal
.fullScreenCover(isPresented: $showModal) {
    ZStack {
        Color.black.opacity(0.3).ignoresSafeArea()

        VStack(spacing: 16) {
            Text("Modal Title")
                .font(.headline)

            Text("Modal content")

            HStack(spacing: 12) {
                Button("Cancel") { showModal = false }
                Button("Confirm") { showModal = false }
            }
        }
        .padding(16)
        .background(Color.white)
        .cornerRadius(12)
    }
}
```

### When to Use Which Pattern
| Pattern | Use Case |
|---------|----------|
| **Tab Bar** | 3-5 main sections at app level |
| **Navigation Drawer** | 5+ sections, deep hierarchy |
| **Bottom Sheet** | Supplementary actions, filters |
| **Modal/Dialog** | Critical decisions, forms, alerts |
| **Navigation Stack** | Forward navigation, back button |

---

## 8. Form Design

### Input Validation
```swift
// SwiftUI form with validation
@State var email = ""
@State var isValidEmail = false

var body: some View {
    VStack(spacing: 16) {
        TextField("Email", text: $email)
            .textInputAutocapitalization(.never)
            .keyboardType(.emailAddress)
            .onChange(of: email) { newValue in
                isValidEmail = validateEmail(newValue)
            }
            .foregroundColor(isValidEmail ? .green : .red)

        if !isValidEmail && !email.isEmpty {
            Label("Invalid email format", systemImage: "exclamationmark.circle")
                .foregroundColor(.red)
                .font(.caption)
        }
    }
}

private func validateEmail(_ email: String) -> Bool {
    let pattern = "[A-Z0-9a-z._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,64}"
    return NSPredicate(format: "SELF MATCHES %@", pattern).evaluate(with: email)
}
```

### Keyboard Handling
```swift
// SwiftUI keyboard toolbar
VStack {
    TextField("Input", text: $text)
        .toolbar {
            ToolbarItemGroup(placement: .keyboard) {
                Spacer()
                Button("Done") {
                    hideKeyboard()
                }
            }
        }
}

// Hide keyboard extension
extension View {
    func hideKeyboard() {
        UIApplication.shared.sendAction(
            #selector(UIResponder.resignFirstResponder),
            to: nil, from: nil, for: nil
        )
    }
}
```

```kotlin
// Compose keyboard handling
var text by remember { mutableStateOf("") }

TextField(
    value = text,
    onValueChange = { text = it },
    keyboardOptions = KeyboardOptions(
        keyboardType = KeyboardType.Email,
        imeAction = ImeAction.Done
    ),
    keyboardActions = KeyboardActions(
        onDone = { /* Handle Done action */ }
    )
)
```

### Auto-fill Support
```swift
// SwiftUI content type hints
TextField("Email", text: $email)
    .textContentType(.emailAddress)

SecureField("Password", text: $password)
    .textContentType(.password)

TextField("Name", text: $name)
    .textContentType(.givenName)
```

### Error States
```swift
// Form with error messages
struct FormField<T>: View {
    var label: String
    var value: Binding<T>
    var error: String?
    var isValid: Bool

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(label)
                .font(.caption)
                .foregroundColor(.gray)

            // Field
            TextField("", text: /* binding */)
                .padding(12)
                .border(
                    isValid ? Color.gray : Color.red,
                    width: 1
                )

            // Error message
            if let error = error {
                HStack(spacing: 4) {
                    Image(systemName: "exclamationmark.circle.fill")
                    Text(error)
                }
                .font(.caption)
                .foregroundColor(.red)
            }
        }
    }
}
```

---

## 9. Loading States

### Skeleton Screens
```swift
// SwiftUI skeleton loading
struct SkeletonCard: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            RoundedRectangle(cornerRadius: 8)
                .fill(Color.gray.opacity(0.3))
                .frame(height: 200)

            RoundedRectangle(cornerRadius: 4)
                .fill(Color.gray.opacity(0.3))
                .frame(height: 16)

            RoundedRectangle(cornerRadius: 4)
                .fill(Color.gray.opacity(0.3))
                .frame(height: 12)
        }
        .padding(16)
    }
}
```

### Shimmer Effect
```swift
// SwiftUI shimmer animation
struct ShimmerView: View {
    @State var isAnimating = false

    var body: some View {
        RoundedRectangle(cornerRadius: 8)
            .fill(Color.gray.opacity(0.3))
            .overlay(
                LinearGradient(
                    gradient: Gradient(colors: [
                        Color.white.opacity(0),
                        Color.white.opacity(0.3),
                        Color.white.opacity(0)
                    ]),
                    startPoint: .leading,
                    endPoint: .trailing
                )
                .offset(x: isAnimating ? 300 : -300)
                .animation(
                    Animation.linear(duration: 1.5).repeatForever(autoreverses: false),
                    value: isAnimating
                )
            )
            .onAppear { isAnimating = true }
    }
}
```

### Pull-to-Refresh
```swift
// SwiftUI refresh control
ScrollView {
    VStack {
        ForEach(items, id: \.self) { item in
            Text(item)
        }
    }
}
.refreshable {
    await fetchData()
}
```

```kotlin
// Compose swipe refresh
var isRefreshing by remember { mutableStateOf(false) }

SwipeRefresh(
    state = rememberSwipeRefreshState(isRefreshing),
    onRefresh = {
        isRefreshing = true
        // Fetch data
    }
) {
    LazyColumn {
        items(items) { item ->
            ItemRow(item)
        }
    }
}
```

### Pagination
```kotlin
// Compose pagination with LazyColumn
LazyColumn(
    state = listState,
    modifier = Modifier.fillMaxSize()
) {
    items(items.size) { index ->
        ItemRow(items[index])

        // Load more when near end
        if (index == items.size - 5) {
            LaunchedEffect(Unit) {
                loadMoreItems()
            }
        }
    }
}
```

---

## 10. Empty & Error States

### Zero-Data Screens
```swift
// Empty state view
struct EmptyStateView: View {
    var title: String
    var subtitle: String
    var actionTitle: String
    var action: () -> Void

    var body: some View {
        VStack(spacing: 24) {
            Image(systemName: "inbox.fill")
                .font(.system(size: 64))
                .foregroundColor(.gray)

            VStack(spacing: 8) {
                Text(title)
                    .font(.headline)
                Text(subtitle)
                    .font(.subheadline)
                    .foregroundColor(.gray)
            }

            Button(action: action) {
                Text(actionTitle)
                    .frame(maxWidth: .infinity)
                    .padding(12)
                    .background(Color.blue)
                    .foregroundColor(.white)
                    .cornerRadius(8)
            }
        }
        .padding(24)
    }
}
```

### Error Recovery UI
```swift
// Error state with retry
struct ErrorStateView: View {
    var error: String
    var retryAction: () -> Void

    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: "exclamationmark.triangle.fill")
                .font(.system(size: 48))
                .foregroundColor(.red)

            Text("Something went wrong")
                .font(.headline)

            Text(error)
                .font(.body)
                .foregroundColor(.gray)
                .multilineTextAlignment(.center)

            HStack(spacing: 12) {
                Button(action: retryAction) {
                    Text("Retry")
                        .frame(maxWidth: .infinity)
                        .padding(12)
                        .background(Color.blue)
                        .foregroundColor(.white)
                        .cornerRadius(8)
                }

                Button("Cancel") {
                    // Close error
                }
                .frame(maxWidth: .infinity)
                .padding(12)
                .border(Color.gray)
                .cornerRadius(8)
            }
        }
        .padding(24)
    }
}
```

---

## 11. Onboarding

### First-Run Experience
```swift
// Onboarding flow
@State var onboardingStep = 0

var body: some View {
    ZStack {
        TabView(selection: $onboardingStep) {
            // Step 1
            VStack(spacing: 24) {
                Image(systemName: "star.fill")
                    .font(.system(size: 64))
                    .foregroundColor(.yellow)
                Text("Welcome")
                    .font(.title)
                Text("This is an awesome app")
                    .foregroundColor(.gray)
                Button("Next") { onboardingStep = 1 }
            }
            .padding(24)
            .tag(0)

            // Step 2
            VStack(spacing: 24) {
                Image(systemName: "bell.fill")
                    .font(.system(size: 64))
                    .foregroundColor(.blue)
                Text("Notifications")
                    .font(.title)
                Text("Stay updated with notifications")
                    .foregroundColor(.gray)
                Button("Next") { onboardingStep = 2 }
            }
            .padding(24)
            .tag(1)
        }
        .tabViewStyle(.page)
    }
}
```

### Progressive Disclosure
```swift
// Show features gradually
@State var completedSteps = Set<String>()

var body: some View {
    VStack(spacing: 16) {
        if completedSteps.contains("profile") {
            Section("Profile") {
                Text("Edit your profile information")
            }
        }

        if completedSteps.contains("preferences") {
            Section("Preferences") {
                Text("Customize your experience")
            }
        }
    }
    .onAppear {
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
            completedSteps.insert("profile")
        }
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) {
            completedSteps.insert("preferences")
        }
    }
}
```

### Permissions Request
```swift
// iOS permissions flow
@State var permissionDenied = false

var body: some View {
    VStack(spacing: 16) {
        Text("Camera Access")
            .font(.headline)

        Text("We need access to your camera")
            .foregroundColor(.gray)

        Button(action: requestCameraPermission) {
            Text("Allow Camera")
                .frame(maxWidth: .infinity)
                .padding(12)
                .background(Color.blue)
                .foregroundColor(.white)
                .cornerRadius(8)
        }

        if permissionDenied {
            Text("Permission was denied")
                .foregroundColor(.red)
        }
    }
}

private func requestCameraPermission() {
    AVCaptureDevice.requestAccess(for: .video) { granted in
        permissionDenied = !granted
    }
}
```

---

## 12. Design Tokens

### Design System Structure
```swift
// Design token hierarchy
struct DesignTokens {
    // Spacing
    struct Spacing {
        static let xs: CGFloat = 4
        static let sm: CGFloat = 8
        static let md: CGFloat = 16
        static let lg: CGFloat = 24
        static let xl: CGFloat = 32
    }

    // Typography
    struct Typography {
        static let displayLarge = Font.system(size: 57, weight: .bold)
        static let headlineMedium = Font.system(size: 28, weight: .bold)
        static let bodyLarge = Font.system(size: 16, weight: .regular)
    }

    // Colors
    struct Colors {
        static let primary = Color(red: 0.4, green: 0.2, blue: 0.8)
        static let secondary = Color(red: 0.2, green: 0.6, blue: 0.9)
        static let error = Color(red: 1.0, green: 0.2, blue: 0.2)
        static let success = Color(red: 0.2, green: 0.8, blue: 0.4)
    }

    // Border radius
    struct BorderRadius {
        static let sm: CGFloat = 4
        static let md: CGFloat = 8
        static let lg: CGFloat = 16
        static let full: CGFloat = .infinity
    }
}

// Usage
VStack(spacing: DesignTokens.Spacing.md) {
    Text("Title")
        .font(DesignTokens.Typography.headlineMedium)
        .foregroundColor(DesignTokens.Colors.primary)
}
.padding(DesignTokens.Spacing.lg)
```

### Token Naming Convention
```
{Category}-{Property}-{State}-{Size}

Examples:
- color-background-default
- color-text-disabled
- spacing-padding-large
- border-radius-medium
- shadow-elevation-high
- font-body-large
- font-headline-small
```

---

## 13. Localization UX

### RTL Support (Right-to-Left)
```swift
// SwiftUI RTL support
HStack(spacing: 12) {
    Image(systemName: "chevron.right")
    Text("Next")
}
.environment(\.layoutDirection, .rightToLeft)

// Automatic for Hebrew, Arabic, Farsi, Urdu
VStack {
    Text("Content") // Auto-flips in RTL languages
}
```

```kotlin
// Compose RTL
CompositionLocalProvider(
    LocalLayoutDirection provides LayoutDirection.Rtl
) {
    Row {
        Icon(Icons.Default.Back, contentDescription = null)
        Text("Back")
    }
}
```

### Text Expansion Handling
```swift
// Account for text expansion in different languages
VStack(spacing: 8) {
    Text("Title")
        .font(.headline)
        .lineLimit(1)
        .truncationMode(.tail)

    Text("Subtitle that may expand in longer languages")
        .font(.caption)
        .lineLimit(3)
        .fixedSize(horizontal: false, vertical: true)
}
.padding(16)

// Set minimum view heights to accommodate expansion
Button(action: {}) {
    Text("Action")
        .frame(minHeight: 44)  // Accounts for larger fonts
}
```

### Cultural Considerations
- **Date/Time Formats**: Use Locale for proper formatting
- **Numbers**: Respect locale-specific number formatting (10,000 vs 10.000)
- **Colors**: Avoid red for errors in some cultures; consider alternatives
- **Gestures**: Swipe left/right may have cultural meanings
- **Icons**: Test culturally sensitive symbols

```swift
// Locale-aware formatting
let formatter = DateFormatter()
formatter.locale = Locale.current
formatter.dateStyle = .medium

let dateString = formatter.string(from: Date())  // "Mar 3, 2026" or "3 mars 2026"

// Number formatting
let numberFormatter = NumberFormatter()
numberFormatter.locale = Locale.current
numberFormatter.numberStyle = .decimal
let formatted = numberFormatter.string(from: 1000) ?? ""  // "1,000" or "1.000"
```

---

## Quick Reference Checklist

- [ ] iOS: 44pt minimum touch targets, SF Symbols for consistency
- [ ] Android: 48dp minimum touch targets, Material 3 components
- [ ] Responsive: Test on notches, Dynamic Island, foldables
- [ ] Typography: Use system fonts, support dynamic type, test expansion
- [ ] Colors: 4.5:1 WCAG contrast, semantic naming, dark mode support
- [ ] Navigation: Choose appropriate patterns for hierarchy depth
- [ ] Forms: Real-time validation, keyboard handling, auto-fill hints
- [ ] Loading: Show skeleton or shimmer, support pull-to-refresh
- [ ] Errors: Provide clear recovery paths, user-friendly messages
- [ ] Onboarding: Progressive disclosure, permissions context
- [ ] Tokens: Centralized system, consistent naming, easy updates
- [ ] i18n: RTL support, text expansion, locale-aware formatting
