# Haptic Feedback Patterns

> Tactile feedback implementation for mobile interfaces

## Why Haptics Matter

- **Confirmation without looking** — Users feel interactions succeeded
- **Reduced cognitive load** — Physical feedback reduces uncertainty
- **Enhanced engagement** — Tactile interactions feel more satisfying
- **Accessibility** — Provides non-visual feedback

---

## Platform Haptic Systems

### iOS Taptic Engine

| Feedback Type | Use Case | Intensity |
|--------------|----------|-----------|
| **Selection** | Picker scrolling, toggles | Light |
| **Impact Light** | Button taps, list items | Light |
| **Impact Medium** | Important actions | Medium |
| **Impact Heavy** | Destructive actions, errors | Heavy |
| **Success** | Task completion | Medium |
| **Warning** | Caution required | Medium |
| **Error** | Failed action | Heavy |

### Android Haptic Constants

| Constant | Use Case |
|----------|----------|
| `EFFECT_TICK` | Light selection |
| `EFFECT_CLICK` | Button press |
| `EFFECT_HEAVY_CLICK` | Important action |
| `EFFECT_DOUBLE_CLICK` | Toggle, confirmation |

---

## Implementation

### iOS (Swift)

```swift
import UIKit

class HapticManager {
    static let shared = HapticManager()
    
    // Selection feedback (light)
    private let selectionGenerator = UISelectionFeedbackGenerator()
    
    // Impact feedback
    private let lightImpact = UIImpactFeedbackGenerator(style: .light)
    private let mediumImpact = UIImpactFeedbackGenerator(style: .medium)
    private let heavyImpact = UIImpactFeedbackGenerator(style: .heavy)
    
    // Notification feedback
    private let notificationGenerator = UINotificationFeedbackGenerator()
    
    func prepare() {
        selectionGenerator.prepare()
        lightImpact.prepare()
        mediumImpact.prepare()
        notificationGenerator.prepare()
    }
    
    func selection() {
        selectionGenerator.selectionChanged()
    }
    
    func impact(_ style: UIImpactFeedbackGenerator.FeedbackStyle = .light) {
        switch style {
        case .light: lightImpact.impactOccurred()
        case .medium: mediumImpact.impactOccurred()
        case .heavy: heavyImpact.impactOccurred()
        default: lightImpact.impactOccurred()
        }
    }
    
    func notification(_ type: UINotificationFeedbackGenerator.FeedbackType) {
        notificationGenerator.notificationOccurred(type)
    }
}

// Usage
HapticManager.shared.impact(.light)  // Button tap
HapticManager.shared.notification(.success)  // Success
HapticManager.shared.notification(.error)  // Error
```

### Android (Kotlin)

```kotlin
import android.content.Context
import android.os.Build
import android.os.VibrationEffect
import android.os.Vibrator
import android.os.VibratorManager
import android.view.HapticFeedbackConstants
import android.view.View

class HapticManager(private val context: Context) {
    
    private val vibrator: Vibrator by lazy {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            val manager = context.getSystemService(Context.VIBRATOR_MANAGER_SERVICE) as VibratorManager
            manager.defaultVibrator
        } else {
            @Suppress("DEPRECATION")
            context.getSystemService(Context.VIBRATOR_SERVICE) as Vibrator
        }
    }
    
    fun tick() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            vibrator.vibrate(VibrationEffect.createPredefined(VibrationEffect.EFFECT_TICK))
        } else {
            vibrator.vibrate(10)
        }
    }
    
    fun click() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            vibrator.vibrate(VibrationEffect.createPredefined(VibrationEffect.EFFECT_CLICK))
        } else {
            vibrator.vibrate(20)
        }
    }
    
    fun heavyClick() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            vibrator.vibrate(VibrationEffect.createPredefined(VibrationEffect.EFFECT_HEAVY_CLICK))
        } else {
            vibrator.vibrate(50)
        }
    }
    
    fun error() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            vibrator.vibrate(VibrationEffect.createWaveform(longArrayOf(0, 50, 50, 50), -1))
        } else {
            vibrator.vibrate(100)
        }
    }
}

// View extension for standard haptic feedback
fun View.performHaptic(feedbackConstant: Int = HapticFeedbackConstants.VIRTUAL_KEY) {
    performHapticFeedback(feedbackConstant)
}
```

### Web (Vibration API)

```javascript
class HapticFeedback {
  static isSupported() {
    return 'vibrate' in navigator;
  }
  
  // Light tap - 10ms
  static tap() {
    if (this.isSupported()) {
      navigator.vibrate(10);
    }
  }
  
  // Medium impact - 20ms
  static impact() {
    if (this.isSupported()) {
      navigator.vibrate(20);
    }
  }
  
  // Heavy impact - 50ms
  static heavyImpact() {
    if (this.isSupported()) {
      navigator.vibrate(50);
    }
  }
  
  // Success pattern
  static success() {
    if (this.isSupported()) {
      navigator.vibrate([10, 50, 10]);
    }
  }
  
  // Error pattern (double buzz)
  static error() {
    if (this.isSupported()) {
      navigator.vibrate([50, 30, 50]);
    }
  }
  
  // Warning (short-long)
  static warning() {
    if (this.isSupported()) {
      navigator.vibrate([10, 30, 50]);
    }
  }
  
  // Selection change (very light)
  static selection() {
    if (this.isSupported()) {
      navigator.vibrate(5);
    }
  }
}

// Usage with buttons
document.querySelectorAll('button').forEach(btn => {
  btn.addEventListener('click', () => HapticFeedback.tap());
});

// Usage with form submission
form.addEventListener('submit', async (e) => {
  e.preventDefault();
  try {
    await submitForm();
    HapticFeedback.success();
  } catch (error) {
    HapticFeedback.error();
  }
});
```

### React Native

```javascript
import { Platform } from 'react-native';
import ReactNativeHapticFeedback from 'react-native-haptic-feedback';

const hapticOptions = {
  enableVibrateFallback: true,
  ignoreAndroidSystemSettings: false,
};

export const Haptics = {
  // Light feedback
  selection: () => {
    ReactNativeHapticFeedback.trigger('selection', hapticOptions);
  },
  
  // Impact feedback
  impactLight: () => {
    ReactNativeHapticFeedback.trigger('impactLight', hapticOptions);
  },
  
  impactMedium: () => {
    ReactNativeHapticFeedback.trigger('impactMedium', hapticOptions);
  },
  
  impactHeavy: () => {
    ReactNativeHapticFeedback.trigger('impactHeavy', hapticOptions);
  },
  
  // Notification feedback
  success: () => {
    ReactNativeHapticFeedback.trigger('notificationSuccess', hapticOptions);
  },
  
  warning: () => {
    ReactNativeHapticFeedback.trigger('notificationWarning', hapticOptions);
  },
  
  error: () => {
    ReactNativeHapticFeedback.trigger('notificationError', hapticOptions);
  },
};

// Usage
<TouchableOpacity 
  onPress={() => {
    Haptics.impactLight();
    handlePress();
  }}
>
  <Text>Press Me</Text>
</TouchableOpacity>
```

---

## Haptic Pattern Guidelines

### When to Use Haptics

| Interaction | Haptic Type | Reason |
|------------|-------------|--------|
| Button tap | Light impact | Confirm press |
| Toggle switch | Selection | State change |
| Slider drag | Selection (continuous) | Position feedback |
| Long-press trigger | Medium impact | Context menu active |
| Swipe action complete | Light impact | Action confirmed |
| Pull-to-refresh | Medium impact | Refresh started |
| Form submit success | Success notification | Task complete |
| Form validation error | Error notification | Attention needed |
| Delete confirmation | Heavy impact | Destructive action |
| Picker scroll | Selection | Value changing |

### When NOT to Use Haptics

- **During scrolling** — Would be overwhelming
- **On every keystroke** — Too frequent
- **Background events** — User didn't initiate
- **Repeatedly in loops** — Annoying
- **When user disabled** — Respect settings

### Haptic Intensity Guidelines

```
Very Light (5-10ms)
├── Scroll picker selection
├── List item highlighting
└── Toggle state change

Light (10-20ms)
├── Button taps
├── Tab switches
└── Swipe actions complete

Medium (20-50ms)
├── Long-press activation
├── Important confirmations
└── Pull-to-refresh trigger

Heavy (50-100ms)
├── Destructive actions
├── Error alerts
└── Critical notifications
```

---

## Respecting User Preferences

### Check System Settings

```javascript
// Web: Reduced motion preference (related to haptics)
const prefersReducedMotion = window.matchMedia(
  '(prefers-reduced-motion: reduce)'
).matches;

// Respect preference
class HapticFeedback {
  static tap() {
    if (prefersReducedMotion) return;
    if ('vibrate' in navigator) {
      navigator.vibrate(10);
    }
  }
}
```

```swift
// iOS: Check if haptics are enabled
func isHapticsEnabled() -> Bool {
    // No direct API, but you can check device capability
    let generator = UIImpactFeedbackGenerator()
    return true // Haptics are automatically disabled on unsupported devices
}
```

```kotlin
// Android: Check vibration settings
fun isHapticsEnabled(context: Context): Boolean {
    val vibrator = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
        val manager = context.getSystemService(Context.VIBRATOR_MANAGER_SERVICE) as VibratorManager
        manager.defaultVibrator
    } else {
        @Suppress("DEPRECATION")
        context.getSystemService(Context.VIBRATOR_SERVICE) as Vibrator
    }
    return vibrator.hasVibrator()
}
```

---

## Testing Haptics

### Test on Real Devices

Haptic feedback cannot be tested in simulators/emulators — only real devices.

### Testing Checklist

- [ ] Haptics fire at correct moments
- [ ] Intensity matches action importance
- [ ] No duplicate/repeated haptics
- [ ] Works when phone is on silent
- [ ] Respects reduced motion preference
- [ ] Pattern distinguishable (success vs error)
- [ ] Not overwhelming during rapid interactions

---

## Key Takeaways

1. **Confirm without visuals** — Haptics confirm action completion
2. **Match intensity to importance** — Heavy for destructive, light for routine
3. **Don't overuse** — Less is more
4. **Test on real devices** — Simulators don't support haptics
5. **Respect preferences** — Some users disable haptics
6. **Consistent patterns** — Same action = same haptic
