# Platform Compliance Checklist

> iOS and Android design guideline conformance

## iOS Compliance (Human Interface Guidelines)

### Navigation
- [ ] Uses iOS navigation patterns (push, modal, tabs)
- [ ] Back navigation via edge swipe
- [ ] Navigation bar follows iOS conventions
- [ ] Tab bar at bottom (if used)
- [ ] No hamburger menu as primary navigation

### Components
- [ ] System controls used where appropriate
- [ ] SF Symbols for icons (or similar style)
- [ ] Native date/time pickers
- [ ] Action sheets for contextual choices
- [ ] Alerts follow iOS pattern

### Touch & Interaction
- [ ] Touch targets ≥44×44pt
- [ ] Standard iOS gestures work
- [ ] Haptic feedback for significant actions
- [ ] No custom scroll physics

### Visual Design
- [ ] Safe areas respected (notch, home indicator)
- [ ] Supports Dynamic Type
- [ ] Dark mode supported
- [ ] SF Pro font or similar sans-serif
- [ ] iOS blur effects where appropriate

### System Integration
- [ ] Supports system-wide features (Share, etc.)
- [ ] Works with iOS accessibility features
- [ ] Respects system settings (text size, motion)
- [ ] Proper keyboard handling

---

## Android Compliance (Material Design 3)

### Navigation
- [ ] Uses Android navigation patterns
- [ ] System back button works correctly
- [ ] Predictive back supported (Android 14+)
- [ ] Navigation drawer or bottom nav
- [ ] Top app bar follows Material pattern

### Components
- [ ] Material Design components used
- [ ] FAB placed correctly (if used)
- [ ] Bottom sheets for secondary content
- [ ] Snackbars for feedback
- [ ] Dialogs follow Material pattern

### Touch & Interaction
- [ ] Touch targets ≥48×48dp
- [ ] Ripple effects on touch
- [ ] Standard Android gestures work
- [ ] Edge-to-edge design

### Visual Design
- [ ] Dynamic Color supported (Android 12+)
- [ ] Material 3 color system
- [ ] Roboto or similar font
- [ ] Proper elevation/shadows
- [ ] Correct icon style (outlined/filled)

### System Integration
- [ ] Works with Android accessibility
- [ ] Respects system settings
- [ ] Proper intent handling
- [ ] Adaptive icons (if app)

---

## Cross-Platform Considerations

### Consistent Behavior
- [ ] Core functionality same on both platforms
- [ ] Data syncs between platforms
- [ ] Account/settings consistent

### Platform-Appropriate Differences
- [ ] Navigation patterns platform-specific
- [ ] Component styling platform-specific
- [ ] Gestures platform-appropriate
- [ ] Typography follows platform convention

### Universal Requirements
- [ ] Accessibility compliant on both
- [ ] Performance optimized for both
- [ ] Offline handling consistent
- [ ] Error handling consistent

---

## Version Support

### iOS
- [ ] Minimum iOS version: ___
- [ ] Tested on current iOS
- [ ] Tested on iOS-1
- [ ] iPad support (if applicable)

### Android
- [ ] Minimum Android version: ___
- [ ] Tested on Android 14
- [ ] Tested on Android 13
- [ ] Tested on various screen sizes
- [ ] Foldable support (if applicable)

---

## Signoff

| Platform | Compliant | Notes |
|----------|-----------|-------|
| iOS | ☐ Yes ☐ No | |
| Android | ☐ Yes ☐ No | |

**Reviewer:** _________________ **Date:** _________________
