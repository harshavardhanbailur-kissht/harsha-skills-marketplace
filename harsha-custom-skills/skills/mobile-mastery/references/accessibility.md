# Mobile Accessibility Reference Guide

Comprehensive guide to implementing WCAG 2.2 compliant accessible mobile applications across iOS, Android, React Native, and Flutter platforms.

## Table of Contents

- [1. WCAG 2.2 Mobile Requirements Overview](#1-wcag-22-mobile-requirements-overview)
- [2. iOS Accessibility Implementation](#2-ios-accessibility-implementation)
- [3. Android Accessibility Implementation](#3-android-accessibility-implementation)
- [4. React Native Accessibility](#4-react-native-accessibility)
- [5. Flutter Accessibility](#5-flutter-accessibility)
- [6. Color Contrast Requirements](#6-color-contrast-requirements)
- [7. Touch Target Sizing](#7-touch-target-sizing)
- [8. Keyboard Navigation & Switch Control](#8-keyboard-navigation--switch-control)
- [9. Reduced Motion Support](#9-reduced-motion-support)
- [10. Focus Management & Accessibility Trees](#10-focus-management--accessibility-trees)
- [11. Automated Accessibility Testing](#11-automated-accessibility-testing)
- [12. Legal Requirements & Compliance](#12-legal-requirements--compliance)

---

## 1. WCAG 2.2 Mobile Requirements Overview

### Perceivable
Content must be perceivable to all users, including those with visual impairments.
- Sufficient color contrast (minimum 4.5:1 for normal text)
- Text alternatives for images and non-text content
- Adaptable content that works with zoom and text scaling
- Distinguishable content (not relying solely on color)

### Operable
Users must be able to navigate and operate the interface.
- Keyboard accessible functionality
- Minimum 44pt touch targets (iOS) / 48dp (Android)
- No time-limited interactions or alternative paths provided
- No seizure-inducing content (no more than 3 flashes per second)

### Understandable
Information and interface operations must be understandable.
- Readable text with clear language
- Predictable navigation patterns
- Input assistance with error prevention and recovery
- Labels and instructions for form inputs

### Robust
Content must be compatible with assistive technologies.
- Valid semantic markup
- ARIA roles and attributes (web-based apps)
- Platform-native accessibility APIs (iOS/Android)
- Proper heading hierarchies

---

## 2. iOS Accessibility Implementation

### VoiceOver Basics
VoiceOver is Apple's screen reader. Enable it in Settings > Accessibility > VoiceOver.

```swift
// Enable/disable VoiceOver programmatically (for testing)
import UIKit

let voiceOverEnabled = UIAccessibility.isVoiceOverRunning
NotificationCenter.default.addObserver(
    forName: UIAccessibility.voiceOverStatusDidChangeNotification,
    object: nil,
    queue: .main
) { _ in
    // Update UI for VoiceOver state
}
```

### SwiftUI Accessibility Modifiers

```swift
import SwiftUI

// Basic accessibility label
Button(action: { /* action */ }) {
    Image(systemName: "heart.fill")
}
.accessibilityLabel("Add to favorites")

// Label with hint
TextField("Email", text: $email)
    .accessibilityLabel("Email address")
    .accessibilityHint("Enter your email address to sign up")

// Custom traits
Button(action: { /* action */ }) {
    Text("Delete Account")
}
.accessibilityAddTraits(.isButton)
.accessibilityRemoveTraits(.isSelected)

// Accessibility container
VStack {
    Text("User Profile")
    Text("Jane Doe")
    Text("Joined March 2024")
}
.accessibilityElement(children: .combine)
.accessibilityLabel("User Profile: Jane Doe, Joined March 2024")

// Hide element from accessibility tree
Image(decorative: "background")
    .accessibilityHidden(true)

// Custom actions
Button(action: { /* action */ }) {
    Text("More Options")
}
.accessibilityAction(.default) {
    // Primary action
}
.accessibilityAction(named: Text("Edit")) {
    // Custom action
}

// Announce changes dynamically
@State private var counter = 0

Button("Increment") {
    counter += 1
    UIAccessibility.post(
        notification: .announcement,
        argument: "Count is now \(counter)"
    )
}
```

### UIKit Accessibility

```swift
import UIKit

class AccessibleViewController: UIViewController {
    let button = UIButton()

    override func viewDidLoad() {
        super.viewDidLoad()

        // Basic accessibility properties
        button.accessibilityLabel = "Save changes"
        button.accessibilityHint = "Double tap to save your changes"
        button.accessibilityIdentifier = "saveButton"

        // Accessibility traits
        button.accessibilityTraits = [.button, .notEnabled]

        // Custom accessibility actions
        button.accessibilityCustomActions = [
            UIAccessibilityCustomAction(
                name: "Delete",
                target: self,
                selector: #selector(deleteAction)
            )
        ]
    }

    @objc func deleteAction() {
        // Handle deletion
    }
}
```

### Dynamic Type Support

```swift
// SwiftUI
Text("Large Title")
    .font(.system(.largeTitle))
    .allowsTightening(true)

// UIKit
let label = UILabel()
label.font = UIFont.preferredFont(forTextStyle: .body)
label.adjustsFontForContentSizeCategory = true
```

### Accessibility Inspector
Use Xcode's Accessibility Inspector (Xcode > Open Developer Tools > Accessibility Inspector) to:
- Inspect accessibility hierarchy
- Verify labels and hints
- Check contrast ratios
- Test with simulated VoiceOver

---

## 3. Android Accessibility Implementation

### TalkBack Basics
TalkBack is Android's screen reader. Enable via Settings > Accessibility > TalkBack.

```kotlin
// Check TalkBack status
val accessibilityManager = context.getSystemService(Context.ACCESSIBILITY_SERVICE)
    as AccessibilityManager
val talkBackEnabled = accessibilityManager.isEnabled

// Listen for TalkBack state changes
val manager: AccessibilityManager = context.getSystemService(ACCESSIBILITY_SERVICE)
    as AccessibilityManager
manager.addAccessibilityStateChangeListener { enabled ->
    // Handle TalkBack state change
}
```

### Jetpack Compose Semantics

```kotlin
import androidx.compose.ui.semantics.*
import androidx.compose.material.Button
import androidx.compose.material.Text

// Basic semantics
Button(onClick = { /* action */ }) {
    Text("Save")
}
.semantics {
    contentDescription = "Save changes"
}

// Role and label
Box(
    modifier = Modifier.semantics {
        role = Role.Button
        contentDescription = "Submit form"
        onClick(label = "Submit") { true }
    }
) {
    Text("Submit")
}

// Custom actions
Button(onClick = { /* action */ }) {
    Text("Options")
}
.semantics {
    customActions = listOf(
        CustomAccessibilityAction(label = "Delete") { true },
        CustomAccessibilityAction(label = "Edit") { true }
    )
}

// Announce live changes
var counter by remember { mutableStateOf(0) }

Button(onClick = { counter++ }) {
    Text("Increment: $counter")
}
.semantics {
    liveRegion = LiveRegionMode.Polite
    contentDescription = "Count: $counter"
}
```

### Legacy XML Layout Accessibility

```xml
<!-- res/layout/activity_main.xml -->
<LinearLayout
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <ImageButton
        android:id="@+id/deleteButton"
        android:layout_width="48dp"
        android:layout_height="48dp"
        android:contentDescription="@string/delete_item"
        android:src="@drawable/ic_delete" />

    <EditText
        android:id="@+id/emailInput"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:contentDescription="@string/email_address"
        android:hint="@string/email_hint" />

</LinearLayout>
```

```kotlin
// Kotlin code for XML layouts
val deleteButton = findViewById<ImageButton>(R.id.deleteButton)
deleteButton.contentDescription = getString(R.string.delete_item)

// Announce live region updates
ViewCompat.announceForAccessibility(
    view,
    "Item deleted successfully"
)
```

### Accessibility Scanner
Run Accessibility Scanner from Google Play to:
- Detect contrast issues
- Identify missing content descriptions
- Check touch target sizes
- Suggest improvements

---

## 4. React Native Accessibility

```javascript
import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  AccessibilityInfo,
  useWindowDimensions,
} from 'react-native';

const AccessibleApp = () => {
  const [count, setCount] = useState(0);

  // Basic accessibility label and hint
  return (
    <View
      accessible={true}
      accessibilityLabel="Counter screen"
      accessibilityRole="header"
    >
      {/* Button with accessibility */}
      <TouchableOpacity
        onPress={() => setCount(count + 1)}
        accessible={true}
        accessibilityLabel="Increment button"
        accessibilityHint="Increments the counter by one"
        accessibilityRole="button"
        accessibilityState={{ disabled: false }}
      >
        <Text>Increment</Text>
      </TouchableOpacity>

      {/* Text with role */}
      <Text
        accessibilityRole="text"
        accessibilityLiveRegion="polite"
        onAccessibilityTap={() => {}}
      >
        Count: {count}
      </Text>

      {/* Custom accessibility actions */}
      <View
        accessible={true}
        accessibilityLabel="Delete button"
        accessibilityActions={[
          { name: 'activate', label: 'Delete item' },
          { name: 'longpress', label: 'More options' },
        ]}
        onAccessibilityAction={(event) => {
          if (event.nativeEvent.actionName === 'activate') {
            // Handle delete
          }
        }}
      >
        <Text>Delete</Text>
      </View>

      {/* Announce changes programmatically */}
      <TouchableOpacity
        onPress={() => {
          setCount(count + 1);
          AccessibilityInfo.announceForAccessibility(
            `Count updated to ${count + 1}`
          );
        }}
      >
        <Text>Update with Announcement</Text>
      </TouchableOpacity>
    </View>
  );
};

export default AccessibleApp;
```

---

## 5. Flutter Accessibility

### Semantics Widget

```dart
import 'package:flutter/material.dart';
import 'package:flutter/semantics.dart';

class AccessibleApp extends StatefulWidget {
  @override
  _AccessibleAppState createState() => _AccessibleAppState();
}

class _AccessibleAppState extends State<AccessibleApp> {
  int _counter = 0;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        appBar: AppBar(title: Text('Accessible App')),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // Basic semantics
              Semantics(
                label: 'Counter display',
                child: Text('Count: $_counter'),
              ),

              // Button with semantics
              Semantics(
                button: true,
                label: 'Increment button',
                hint: 'Increments the counter',
                onTap: () => setState(() => _counter++),
                child: Material(
                  child: InkWell(
                    onTap: () => setState(() => _counter++),
                    child: Text('Increment'),
                  ),
                ),
              ),

              // Custom actions
              Semantics(
                customSemanticsActions: {
                  CustomSemanticsAction(label: 'Delete'): () {
                    setState(() => _counter = 0);
                  },
                },
                child: Container(
                  child: Text('Custom Action Button'),
                ),
              ),

              // Live region announcement
              Semantics(
                liveRegion: true,
                child: Text('Status: Updated'),
              ),

              // Image with label
              Semantics(
                image: true,
                label: 'App logo',
                child: Image.asset('assets/logo.png'),
              ),

              // Skip navigation
              Semantics(
                enabled: true,
                onTap: () {},
                child: Text('Skip to main content'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
```

### SemanticsService for Announcements

```dart
import 'package:flutter/services.dart';

class AccessibleWidget extends StatelessWidget {
  void _announceUpdate(String message) {
    SemanticsService.announce(message);
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () {
        _announceUpdate('Item selected successfully');
      },
      child: Container(
        child: Text('Tap me'),
      ),
    );
  }
}
```

---

## 6. Color Contrast Requirements

### WCAG AA Standards (Minimum)
- **Normal text**: 4.5:1 contrast ratio
- **Large text** (18pt+ or 14pt+ bold): 3:1 contrast ratio
- **UI components**: 3:1 contrast ratio

### Contrast Checking Tools

```swift
// Swift: Calculate contrast ratio
func contrastRatio(foreground: UIColor, background: UIColor) -> CGFloat {
    let foreRGB = foreground.cgColor.components ?? [0, 0, 0, 1]
    let backRGB = background.cgColor.components ?? [1, 1, 1, 1]

    let foreL = relativeLuminance(r: foreRGB[0], g: foreRGB[1], b: foreRGB[2])
    let backL = relativeLuminance(r: backRGB[0], g: backRGB[1], b: backRGB[2])

    let lighter = max(foreL, backL)
    let darker = min(foreL, backL)

    return (lighter + 0.05) / (darker + 0.05)
}

func relativeLuminance(r: CGFloat, g: CGFloat, b: CGFloat) -> CGFloat {
    let rs = r <= 0.03928 ? r / 12.92 : pow((r + 0.055) / 1.055, 2.4)
    let gs = g <= 0.03928 ? g / 12.92 : pow((g + 0.055) / 1.055, 2.4)
    let bs = b <= 0.03928 ? b / 12.92 : pow((b + 0.055) / 1.055, 2.4)

    return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs
}
```

### Design Best Practices
- Don't rely on color alone to convey information
- Use patterns, icons, or text labels alongside colors
- Test with color blindness simulators
- Verify contrast in all states (normal, hover, focus, disabled)

---

## 7. Touch Target Sizing

### Platform Standards
- **iOS**: Minimum 44pt × 44pt (≈11.6mm × 11.6mm)
- **Android**: Minimum 48dp × 48dp (≈9mm × 9mm)

```swift
// SwiftUI
Button(action: { /* action */ }) {
    Text("Tap me")
}
.frame(minHeight: 44)
.contentShape(Rectangle())
```

```kotlin
// Compose
Button(
    onClick = { /* action */ },
    modifier = Modifier.size(width = 48.dp, height = 48.dp)
) {
    Text("Tap")
}
```

```xml
<!-- XML Layout -->
<Button
    android:layout_width="48dp"
    android:layout_height="48dp"
    android:layout_margin="8dp"
    android:text="Tap me" />
```

### Spacing Between Targets
- Minimum 8pt/dp spacing between interactive elements
- Use padding or margins to increase target area without extending visual size

---

## 8. Keyboard Navigation & Switch Control

### iOS
```swift
// Enable keyboard navigation
override var canBecomeFirstResponder: Bool { true }

// SwiftUI keyboard shortcut
Button(action: { /* action */ }) {
    Text("Save")
}
.keyboardShortcut(.defaultAction)

// Custom key commands
override var keyCommands: [UIKeyCommand]? {
    return [
        UIKeyCommand(input: "s", modifierFlags: .command,
                     action: #selector(saveAction)),
        UIKeyCommand(input: UIKeyCommand.inputDelete,
                     action: #selector(deleteAction))
    ]
}

// Switch Control support
button.isAccessibilityElement = true
button.accessibilityTraits = .button
```

### Android
```kotlin
// Keyboard navigation with Focus
modifier = Modifier
    .focusable()
    .onKeyEvent { keyEvent ->
        when {
            keyEvent.key == Key.Enter -> {
                // Handle Enter
                true
            }
            else -> false
        }
    }

// Custom focus behavior
FocusRequester().requestFocus()

// Traverse focus order
modifier = Modifier.focusOrder(focusRequester) { next ->
    next(FocusDirection.Down)
}
```

---

## 9. Reduced Motion Support

### iOS
```swift
import UIKit

let prefersReducedMotion = UIAccessibility.isReduceMotionEnabled

// SwiftUI
@Environment(\.accessibilityReduceMotion) var reduceMotion

if reduceMotion {
    // Disable animations
    withAnimation(.none) {
        // State change
    }
} else {
    // Normal animation
    withAnimation(.easeInOut) {
        // State change
    }
}

// Listen for changes
NotificationCenter.default.addObserver(
    forName: UIAccessibility.reduceMotionStatusDidChangeNotification,
    object: nil,
    queue: .main
) { _ in
    // Handle motion preference change
}
```

### Android
```kotlin
import android.content.Context
import android.provider.Settings

val prefersReducedMotion = Settings.Global.getFloat(
    context.contentResolver,
    Settings.Global.ANIMATOR_DURATION_SCALE,
    1f
) == 0f

// Jetpack Compose
val reduceMotion = LocalConfiguration.current.run {
    // Check accessibility settings
    android.provider.Settings.Global.getFloat(
        context.contentResolver,
        android.provider.Settings.Global.ANIMATOR_DURATION_SCALE, 1f
    ) == 0f
}

if (reduceMotion) {
    // Skip animations
} else {
    // Use animations
}
```

### React Native
```javascript
import { AccessibilityInfo, useWindowDimensions } from 'react-native';
import { usePrefers } from 'react-native-web';

const prefersReducedMotion = usePrefers('prefers-reduced-motion') === 'reduce';

<Animated.View
  style={[
    {
      opacity: prefersReducedMotion
        ? new Animated.Value(1)
        : animatedOpacity,
    },
  ]}
>
  {/* Content */}
</Animated.View>
```

---

## 10. Focus Management & Accessibility Trees

### iOS VoiceOver Focus
```swift
// Set initial focus
override var preferredFocusEnvironments: [UIFocusEnvironment] {
    return [searchField]
}

// SwiftUI
TextField("Search", text: $query)
    .focused($focusedField, equals: .search)
    .onAppear {
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
            self.focusedField = .search
        }
    }

// Manual focus restoration
UIAccessibility.post(
    notification: .layoutChanged,
    argument: confirmButton
)
```

### Android TalkBack Focus
```kotlin
// Request focus
view.requestFocus()

// Set accessibility focus
view.sendAccessibilityEvent(AccessibilityEvent.TYPE_VIEW_FOCUSED)

// Custom focus traversal
view.nextFocusRightId = R.id.next_button
view.nextFocusDownId = R.id.next_field

// Announce focus changes
ViewCompat.announceForAccessibility(view, "Focused on $description")
```

### Accessibility Tree Verification
```swift
// SwiftUI view debugger
Text("Element")
    .accessibilityElement(children: .combine)
    .debugDescription // Check tree in console

// UIKit
let element = button as UIAccessibilityElement
print("Label: \(element.accessibilityLabel ?? "")")
print("Traits: \(element.accessibilityTraits)")
```

---

## 11. Automated Accessibility Testing

### XCTest (iOS)
```swift
import XCTest

class AccessibilityTests: XCTestCase {
    func testVoiceOverElements() {
        let app = XCUIApplication()
        app.launch()

        // Check element is accessible
        let button = app.buttons["Save Button"]
        XCTAssertTrue(button.isAccessibilityElement)
        XCTAssertNotNil(button.label)
        XCTAssertEqual(button.label, "Save changes")

        // Verify traits
        let traits = button.traits
        XCTAssertTrue(traits.contains(.button))
    }

    func testDynamicType() {
        let app = XCUIApplication()
        app.launchArguments = ["-com.apple.accessibility.spoken-feedback"]
        app.launch()
    }
}
```

### Espresso (Android)
```kotlin
import androidx.test.espresso.Espresso.onView
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.google.android.apps.common.testing.accessibility.framework.AccessibilityCheckRunner

@RunWith(AndroidJUnit4::class)
class AccessibilityTests {
    @Test
    fun testAccessibilityChecks() {
        val activity = activityScenario.result.rootActivity as Activity
        AccessibilityCheckRunner.runChecks(activity)
    }
}
```

### Compose Testing
```kotlin
@get:Rule
val composeTestRule = createComposeRule()

@Test
fun testSemantics() {
    composeTestRule.setContent {
        Button(onClick = {}, modifier = Modifier.semantics {
            contentDescription = "Test Button"
        }) {
            Text("Click Me")
        }
    }

    composeTestRule
        .onNodeWithContentDescription("Test Button")
        .assertExists()
        .performClick()
}
```

### Flutter Testing
```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/semantics.dart';

void main() {
  testWidgets('Verify semantics', (WidgetTester tester) async {
    await tester.pumpWidget(MyApp());

    expect(
      find.bySemanticsLabel('Increment button'),
      findsOneWidget,
    );

    await tester.tap(find.bySemanticsLabel('Increment button'));
    await tester.pump();
  });
}
```

### Automated Testing Tools
- **WebAIM Contrast Checker**: Verify color contrast
- **axe DevTools**: Mobile web accessibility audit
- **Lighthouse**: Automated accessibility audit
- **Accessibility Inspector**: Native platform tools

---

## 12. Legal Requirements & Compliance

### Americans with Disabilities Act (ADA)
- Applies to public accommodations, government agencies, and businesses
- Mobile apps must provide equal access to services
- Covered under Title II and Title III
- No explicit safe harbor for mobile apps

### European Accessibility Act (EAA)
- Effective 2025 for most businesses, 2030 for micro-enterprises
- Requires accessibility of digital products and services
- WCAG 2.1 Level AA minimum compliance
- Applies throughout EU

### WCAG 2.2 Compliance Levels
- **Level A**: Basic accessibility
- **Level AA**: Enhanced accessibility (recommended minimum)
- **Level AAA**: Advanced accessibility

### Compliance Checklist
- [ ] Conduct accessibility audit
- [ ] Implement accessibility features
- [ ] Test with assistive technologies
- [ ] Document accessibility statement
- [ ] Train development team
- [ ] Establish accessibility feedback mechanism
- [ ] Perform regular audits
- [ ] Fix issues promptly
- [ ] Maintain accessibility over time

### Documentation Requirements
```markdown
## Accessibility Statement

This application is committed to accessibility and usability
for all users, including those with disabilities.

### Features:
- VoiceOver support (iOS)
- TalkBack support (Android)
- Keyboard navigation
- Color contrast compliance (WCAG AA)
- Adjustable text sizing

### Known Issues:
[Document any limitations]

### Feedback:
Contact accessibility@company.com for accessibility issues
```

---

## Quick Reference: Platform Checklist

### iOS (SwiftUI)
- [ ] `.accessibilityLabel` on all interactive elements
- [ ] `.accessibilityHint` for complex interactions
- [ ] `Dynamic Type` support enabled
- [ ] `.accessibilityHidden(true)` for decorative images
- [ ] Color contrast 4.5:1 minimum
- [ ] Touch targets 44pt minimum
- [ ] VoiceOver tested with Accessibility Inspector

### Android (Compose)
- [ ] `contentDescription` on images
- [ ] `semantics { role = Role.Button }` on interactive elements
- [ ] `liveRegion` for announcements
- [ ] Contrast 4.5:1 minimum
- [ ] Touch targets 48dp minimum
- [ ] TalkBack tested with Accessibility Scanner

### React Native
- [ ] `accessibilityLabel` on all components
- [ ] `accessibilityRole` specified
- [ ] `accessibilityState` for interactive elements
- [ ] Announcements for dynamic updates
- [ ] Platform-specific testing

### Flutter
- [ ] `Semantics` widget wrapping key elements
- [ ] `label` and `hint` provided
- [ ] `button: true` for button-like widgets
- [ ] `liveRegion` for announcements
- [ ] `SemanticsService.announce()` for feedback

---

## Resources

- [WCAG 2.2 Guidelines](https://www.w3.org/WAI/WCAG22/quickref/)
- [Apple Accessibility Documentation](https://developer.apple.com/accessibility/)
- [Android Accessibility Documentation](https://developer.android.com/guide/topics/ui/accessibility)
- [React Native Accessibility](https://reactnative.dev/docs/accessibility)
- [Flutter Semantics](https://flutter.dev/docs/development/accessibility-and-localization/accessibility)
- [WebAIM Resources](https://webaim.org/)
- [Deque University](https://dequeuniversity.com/)
