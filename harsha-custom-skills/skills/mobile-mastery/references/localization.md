# Mobile App Localization Reference Guide

Comprehensive guide to implementing localization across iOS, Android, React Native, and Flutter platforms with best practices for RTL support, formatters, and dynamic language switching.

## Table of Contents
1. [iOS Localization](#ios-localization)
2. [Android Localization](#android-localization)
3. [React Native Localization](#react-native-localization)
4. [Flutter Localization](#flutter-localization)
5. [RTL Layout Support](#rtl-layout-support)
6. [Locale-Aware Formatting](#locale-aware-formatting)
7. [Dynamic Language Switching](#dynamic-language-switching)
8. [Translation Management Platforms](#translation-management-platforms)
9. [Pseudo-Localization](#pseudo-localization)
10. [App Store Metadata](#app-store-metadata)
11. [Cultural Considerations](#cultural-considerations)

---

## iOS Localization

### String Catalogs (Xcode 15+)

String Catalogs provide a modern, unified approach to managing localizations in iOS 15+ apps.

```swift
// Enable String Catalogs in Xcode:
// 1. File → New → String Catalog
// 2. Name it "Localizable.xcstrings"
// 3. Supports automatic extraction and management

// Usage in code:
import SwiftUI

struct ContentView: View {
    var body: some View {
        VStack {
            Text("hello_world")  // Extracted to String Catalog
            Text("welcome_message")
            Button("save_changes") {
                saveData()
            }
        }
    }
}

// String Catalog JSON structure (Localizable.xcstrings):
{
  "sourceLanguage": "en",
  "strings": {
    "hello_world": {
      "comment": "Main greeting displayed to user",
      "extractionState": "manual",
      "localizations": {
        "en": {
          "stringUnit": {
            "state": "translated",
            "value": "Hello, World!"
          }
        },
        "es": {
          "stringUnit": {
            "state": "translated",
            "value": "¡Hola, Mundo!"
          }
        },
        "fr": {
          "stringUnit": {
            "state": "translated",
            "value": "Bonjour, Monde!"
          }
        }
      }
    }
  }
}
```

### NSLocalizedString (Legacy)

Traditional approach for iOS apps pre-Xcode 15.

```swift
// Basic localization
let greeting = NSLocalizedString(
    "hello_world",
    comment: "Main greeting"
)

// With table parameter
let message = NSLocalizedString(
    "welcome_message",
    tableName: "WelcomeScreen",
    bundle: Bundle.main,
    value: "Welcome!",
    comment: "Welcome message on app launch"
)

// Localizable.strings file (English):
"hello_world" = "Hello, World!";
"welcome_message" = "Welcome to our app!";
"settings_title" = "Settings";

// Localizable.strings file (Spanish):
"hello_world" = "¡Hola, Mundo!";
"welcome_message" = "¡Bienvenido a nuestra aplicación!";
"settings_title" = "Configuración";
```

### Stringsdict Plurals

Handle plural forms correctly for different locales.

```swift
// Localizable.stringsdict XML structure:
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
    "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>items_count</key>
    <dict>
        <key>NSStringLocalizedFormatKey</key>
        <string>%#@item_count@</string>
        <key>item_count</key>
        <dict>
            <key>NSStringFormatSpecTypeKey</key>
            <string>NSStringPluralRuleType</string>
            <key>NSStringFormatValueTypeKey</key>
            <string>d</string>
            <key>one</key>
            <string>%d item</string>
            <key>other</key>
            <string>%d items</string>
        </dict>
    </dict>
    <key>friends_count</key>
    <dict>
        <key>NSStringLocalizedFormatKey</key>
        <string>You have %#@friend_count@</string>
        <key>friend_count</key>
        <dict>
            <key>NSStringFormatSpecTypeKey</key>
            <string>NSStringPluralRuleType</string>
            <key>NSStringFormatValueTypeKey</key>
            <string>d</string>
            <key>zero</key>
            <string>no friends</string>
            <key>one</key>
            <string>%d friend</string>
            <key>other</key>
            <string>%d friends</string>
        </dict>
    </dict>
</dict>
</plist>

// Usage in Swift:
let itemCount = 5
let formatted = String(format: NSLocalizedString("items_count", comment: ""), itemCount)
// Output: "5 items"
```

### Info.plist Localization

Localize app name and configuration strings.

```xml
<!-- Info.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
    "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDisplayName</key>
    <string>$(PRODUCT_NAME)</string>
    <key>CFBundleLocalizations</key>
    <array>
        <string>en</string>
        <string>es</string>
        <string>fr</string>
        <string>de</string>
        <string>ja</string>
        <string>ar</string>
    </array>
    <key>NSLocalizedString</key>
    <string>Localized strings</string>
</dict>
</plist>

<!-- InfoPlist.strings (English) -->
CFBundleDisplayName = "MyApp";
NSCameraUsageDescription = "We need camera access for video calls";
NSPhotoLibraryUsageDescription = "We need access to your photos";

<!-- InfoPlist.strings (Spanish) -->
CFBundleDisplayName = "MiAplicación";
NSCameraUsageDescription = "Necesitamos acceso a la cámara para videollamadas";
NSPhotoLibraryUsageDescription = "Necesitamos acceso a tus fotos";
```

### Asset Localization

Localize images and other assets.

```swift
// In Xcode:
// 1. Select image asset in Assets catalog
// 2. In Attributes Inspector, set "Localization" dropdown
// 3. Add localized versions for each language

// Using localized assets in code:
struct LocalizedAssetExample: View {
    var body: some View {
        VStack {
            // System automatically loads correct version
            Image("welcome_image")  // Loads en/welcome_image, es/welcome_image, etc.
            Image(systemName: "globe")
        }
    }
}

// Programmatic asset selection
func getLocalizedImage(_ name: String) -> UIImage? {
    let currentLanguage = NSLocale.preferredLanguages[0]
    let languageCode = currentLanguage.split(separator: "-")[0]

    if let image = UIImage(named: "\(languageCode)/\(name)") {
        return image
    }
    return UIImage(named: name)  // Fallback to base image
}
```

### Date/Number/Currency Formatters

Locale-aware formatting for different data types.

```swift
import Foundation

// Date Formatting
let date = Date()
let dateFormatter = DateFormatter()
dateFormatter.locale = Locale.current
dateFormatter.dateStyle = .long
dateFormatter.timeStyle = .medium
let formattedDate = dateFormatter.string(from: date)
// Output varies by locale: "March 3, 2026" (en) vs "3 de marzo de 2026" (es)

// Using DateComponentsFormatter
let calendar = Calendar.current
let components = calendar.dateComponents([.year, .month, .day], from: date)
let componentsFormatter = DateComponentsFormatter()
componentsFormatter.allowedUnits = [.year, .month, .day]
componentsFormatter.unitsStyle = .full
let formatted = componentsFormatter.string(from: components)

// Number Formatting
let number = 1234567.89
let numberFormatter = NumberFormatter()
numberFormatter.locale = Locale.current
numberFormatter.numberStyle = .decimal
numberFormatter.minimumFractionDigits = 2
numberFormatter.maximumFractionDigits = 2
let formattedNumber = numberFormatter.string(from: NSNumber(value: number))
// Output: "1,234,567.89" (en) vs "1.234.567,89" (de)

// Currency Formatting
let currencyFormatter = NumberFormatter()
currencyFormatter.locale = Locale.current
currencyFormatter.numberStyle = .currency
currencyFormatter.currencyCode = "USD"
let formattedCurrency = currencyFormatter.string(from: NSNumber(value: 99.99))
// Output: "$99.99" (en-US) vs "99,99 USD" (de-DE)

// Percentage Formatting
let percentFormatter = NumberFormatter()
percentFormatter.locale = Locale.current
percentFormatter.numberStyle = .percent
let formattedPercent = percentFormatter.string(from: NSNumber(value: 0.85))
// Output: "85%" (en) vs "85 %" (fr)
```

---

## Android Localization

### Strings.xml Structure

Organize localized strings by language.

```xml
<!-- res/values/strings.xml (English - default) -->
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">MyApp</string>
    <string name="hello_world">Hello, World!</string>
    <string name="welcome_message">Welcome to our app!</string>
    <string name="settings_title">Settings</string>
    <string name="user_greeting">Hello, %1$s</string>
    <string name="items_in_cart">You have %1$d items in your cart</string>
</resources>

<!-- res/values-es/strings.xml (Spanish) -->
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">MiAplicación</string>
    <string name="hello_world">¡Hola, Mundo!</string>
    <string name="welcome_message">¡Bienvenido a nuestra aplicación!</string>
    <string name="settings_title">Configuración</string>
    <string name="user_greeting">Hola, %1$s</string>
    <string name="items_in_cart">Tienes %1$d artículos en tu carrito</string>
</resources>

<!-- res/values-fr/strings.xml (French) -->
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">MonApplication</string>
    <string name="hello_world">Bonjour, Monde!</string>
    <string name="welcome_message">Bienvenue dans notre application!</string>
    <string name="settings_title">Paramètres</string>
    <string name="user_greeting">Bonjour, %1$s</string>
    <string name="items_in_cart">Vous avez %1$d articles dans votre panier</string>
</resources>

<!-- res/values-ja/strings.xml (Japanese) -->
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">マイアプリ</string>
    <string name="hello_world">こんにちは、世界！</string>
    <string name="welcome_message">当アプリへようこそ！</string>
    <string name="settings_title">設定</string>
    <string name="user_greeting">こんにちは、%1$sさん</string>
    <string name="items_in_cart">カートに%1$d件の商品があります</string>
</resources>
```

### Plurals

Handle plural forms correctly.

```xml
<!-- res/values/plurals.xml -->
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <plurals name="items_count">
        <item quantity="one">%d item</item>
        <item quantity="other">%d items</item>
    </plurals>
    <plurals name="friends_count">
        <item quantity="zero">No friends</item>
        <item quantity="one">%d friend</item>
        <item quantity="other">%d friends</item>
    </plurals>
    <plurals name="notification_count">
        <item quantity="one">You have %d new message</item>
        <item quantity="other">You have %d new messages</item>
    </plurals>
</resources>

<!-- res/values-es/plurals.xml -->
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <plurals name="items_count">
        <item quantity="one">%d artículo</item>
        <item quantity="other">%d artículos</item>
    </plurals>
    <plurals name="friends_count">
        <item quantity="zero">Sin amigos</item>
        <item quantity="one">%d amigo</item>
        <item quantity="other">%d amigos</item>
    </plurals>
    <plurals name="notification_count">
        <item quantity="one">Tienes %d nuevo mensaje</item>
        <item quantity="other">Tienes %d nuevos mensajes</item>
    </plurals>
</resources>
```

### String Arrays

Localize arrays of strings.

```xml
<!-- res/values/arrays.xml -->
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string-array name="days_of_week">
        <item>Sunday</item>
        <item>Monday</item>
        <item>Tuesday</item>
        <item>Wednesday</item>
        <item>Thursday</item>
        <item>Friday</item>
        <item>Saturday</item>
    </string-array>
    <string-array name="months">
        <item>January</item>
        <item>February</item>
        <item>March</item>
        <!-- ... -->
    </string-array>
</resources>

<!-- res/values-es/arrays.xml -->
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string-array name="days_of_week">
        <item>Domingo</item>
        <item>Lunes</item>
        <item>Martes</item>
        <item>Miércoles</item>
        <item>Jueves</item>
        <item>Viernes</item>
        <item>Sábado</item>
    </string-array>
    <string-array name="months">
        <item>Enero</item>
        <item>Febrero</item>
        <item>Marzo</item>
        <!-- ... -->
    </string-array>
</resources>
```

### Per-App Language Preference (API 33+)

Set language preferences per app without changing system language.

```kotlin
// MainActivity.kt
import android.os.LocaleList
import androidx.appcompat.app.AppCompatDelegate

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Set app language to Spanish (API 33+)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            val locales = LocaleList(Locale("es"))
            AppCompatDelegate.setApplicationLocales(locales)
        }

        setContentView(R.layout.activity_main)
    }
}

// Utility function for language switching
object LocaleManager {
    fun setAppLanguage(context: Context, languageCode: String) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            val locale = Locale(languageCode)
            AppCompatDelegate.setApplicationLocales(LocaleList(locale))
        } else {
            // Fallback for older versions
            val locale = Locale(languageCode)
            val config = Configuration()
            config.locale = locale
            context.resources.updateConfiguration(config, context.resources.displayMetrics)
        }
    }

    fun getAppLanguage(context: Context): String {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            val locales = context.getSystemService(LocaleManager::class.java).applicationLocales
            locales.get(0)?.language ?: Locale.getDefault().language
        } else {
            Locale.getDefault().language
        }
    }
}
```

### Android Resource Usage

```kotlin
// Activity/Fragment usage
class HomeActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_home)

        val greeting = getString(R.string.hello_world)
        val userGreeting = getString(R.string.user_greeting, "John")

        val itemCount = 5
        val plural = resources.getQuantityString(
            R.plurals.items_count,
            itemCount,
            itemCount
        )

        val daysArray = resources.getStringArray(R.array.days_of_week)
    }
}
```

---

## React Native Localization

### react-i18next Setup

Modern localization library with powerful features.

```bash
npm install i18next react-i18next expo-localization
```

```javascript
// i18n/config.js
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import * as Localization from 'expo-localization';

// Import translation files
import enTranslations from './locales/en.json';
import esTranslations from './locales/es.json';
import frTranslations from './locales/fr.json';
import jaTranslations from './locales/ja.json';
import arTranslations from './locales/ar.json';

const resources = {
    en: { translation: enTranslations },
    es: { translation: esTranslations },
    fr: { translation: frTranslations },
    ja: { translation: jaTranslations },
    ar: { translation: arTranslations },
};

// Get device locale
const deviceLanguage = Localization.locale.split('-')[0];

i18n
    .use(initReactI18next)
    .init({
        resources,
        lng: deviceLanguage,
        fallbackLng: 'en',
        interpolation: {
            escapeValue: false,
        },
        detection: {
            order: ['localStorage', 'navigator'],
            caches: ['localStorage'],
        },
    });

export default i18n;

// locales/en.json
{
  "hello_world": "Hello, World!",
  "welcome_message": "Welcome to our app!",
  "user_greeting": "Hello, {{name}}!",
  "items_count": "You have {{count}} item",
  "items_count_plural": "You have {{count}} items",
  "settings": {
    "title": "Settings",
    "language": "Language",
    "theme": "Theme"
  }
}

// locales/es.json
{
  "hello_world": "¡Hola, Mundo!",
  "welcome_message": "¡Bienvenido a nuestra aplicación!",
  "user_greeting": "¡Hola, {{name}}!",
  "items_count": "Tienes {{count}} artículo",
  "items_count_plural": "Tienes {{count}} artículos",
  "settings": {
    "title": "Configuración",
    "language": "Idioma",
    "theme": "Tema"
  }
}
```

### Component Usage

```javascript
// App.js
import './i18n/config';
import { useTranslation } from 'react-i18next';
import { View, Text, Button } from 'react-native';

export default function App() {
    const { i18n, t } = useTranslation();

    return (
        <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
            <Text>{t('hello_world')}</Text>
            <Text>{t('user_greeting', { name: 'John' })}</Text>
            <Text>{t('items_count', { count: 5 })}</Text>

            <Button
                title={t('settings.language')}
                onPress={() => changeLanguage('es')}
            />
        </View>
    );
}

function changeLanguage(languageCode) {
    i18n.changeLanguage(languageCode);
    // Save preference to AsyncStorage
    AsyncStorage.setItem('userLanguage', languageCode);
}
```

### Expo-Localization Integration

```javascript
import * as Localization from 'expo-localization';
import { I18n } from 'i18n-js';

const translations = {
    en: { hello: 'Hello' },
    es: { hello: 'Hola' },
    fr: { hello: 'Bonjour' },
};

const i18n = new I18n(translations);
i18n.locale = Localization.locale;
i18n.enableFallback = true;

console.log(i18n.t('hello')); // Uses device locale
```

### React-Native-Localize

```bash
npm install react-native-localize
```

```javascript
import RNLocalize from 'react-native-localize';

const locales = RNLocalize.getLocales();
console.log(locales);
// Output: [{ languageCode: 'en', countryCode: 'US' }]

const preferredLanguage = RNLocalize.findBestAvailableLanguage(['en', 'es', 'fr']);
console.log(preferredLanguage);
// Output: { languageTag: 'en', isRTL: false }

// Handle RTL languages
const isRTL = RNLocalize.isRTL;
if (isRTL) {
    I18nManager.forceRTL(true);
}
```

---

## Flutter Localization

### Intl Package Setup

```yaml
# pubspec.yaml
dependencies:
  flutter_localizations:
    sdk: flutter
  intl: ^0.19.0

dev_dependencies:
  intl_translation: ^0.18.0

# Enable generation
flutter_intl:
  enabled: true
```

### Message Definitions

```dart
// lib/l10n/messages_en.arb
{
  "@@locale": "en",
  "helloWorld": "Hello, World!",
  "welcomeMessage": "Welcome to our app!",
  "userGreeting": "Hello, {name}!",
  "@userGreeting": {
    "description": "Greeting with user name",
    "placeholders": {
      "name": {
        "type": "String",
        "example": "John"
      }
    }
  },
  "itemsCount": "{count, plural, =0{No items} =1{One item} other{{count} items}}",
  "@itemsCount": {
    "description": "Plural items count",
    "placeholders": {
      "count": {
        "type": "int",
        "format": "compact"
      }
    }
  }
}

// lib/l10n/messages_es.arb
{
  "@@locale": "es",
  "helloWorld": "¡Hola, Mundo!",
  "welcomeMessage": "¡Bienvenido a nuestra aplicación!",
  "userGreeting": "¡Hola, {name}!",
  "itemsCount": "{count, plural, =0{Sin artículos} =1{Un artículo} other{{count} artículos}}"
}

// lib/l10n/messages_fr.arb
{
  "@@locale": "fr",
  "helloWorld": "Bonjour, Monde!",
  "welcomeMessage": "Bienvenue dans notre application!",
  "userGreeting": "Bonjour, {name}!",
  "itemsCount": "{count, plural, =0{Aucun article} =1{Un article} other{{count} articles}}"
}

// lib/l10n/messages_ar.arb
{
  "@@locale": "ar",
  "helloWorld": "مرحبا بالعالم!",
  "welcomeMessage": "أهلا وسهلا بك في تطبيقنا!",
  "userGreeting": "مرحبا، {name}!",
  "itemsCount": "{count, plural, =0{لا توجد عناصر} =1{عنصر واحد} other{{count} عناصر}}"
}
```

### ARB Files Structure

```json
{
  "@@locale": "en",
  "@@author": "Your Name",
  "@@version": "1.0.0",
  "appName": "MyApp",
  "@appName": {
    "description": "Application name"
  },
  "helloWorld": "Hello, World!",
  "@helloWorld": {
    "context": "greeting",
    "description": "Main greeting message"
  },
  "dateFormat": "MMM d, y",
  "timeFormat": "h:mm a",
  "currencySymbol": "$"
}
```

### Gen-L10n Usage

```dart
// lib/main.dart
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'l10n/messages_all.dart';
import 'generated/l10n.dart';

void main() => runApp(const MyApp());

class MyApp extends StatelessWidget {
    const MyApp({Key? key}) : super(key: key);

    @override
    Widget build(BuildContext context) {
        return MaterialApp(
            title: 'Localization Demo',
            localizationsDelegates: [
                S.delegate,
                GlobalMaterialLocalizations.delegate,
                GlobalCupertinoLocalizations.delegate,
                GlobalWidgetsLocalizations.delegate,
            ],
            supportedLocales: S.delegate.supportedLocales,
            home: const HomePage(),
        );
    }
}

// lib/screens/home_screen.dart
class HomePage extends StatelessWidget {
    const HomePage({Key? key}) : super(key: key);

    @override
    Widget build(BuildContext context) {
        final l10n = S.of(context);

        return Scaffold(
            appBar: AppBar(title: Text(l10n.appName)),
            body: Center(
                child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                        Text(l10n.helloWorld),
                        Text(l10n.userGreeting(name: 'John')),
                        Text(l10n.itemsCount(count: 5)),
                    ],
                ),
            ),
        );
    }
}
```

### Intl Formatting

```dart
import 'package:intl/intl.dart';
import 'l10n/messages_all.dart';
import 'generated/l10n.dart';

class FormattingExample {
    static void demonstrateFormatting(BuildContext context) {
        // Date formatting
        final dateFormat = DateFormat('MMMM d, y', 'en_US');
        final formattedDate = dateFormat.format(DateTime.now());
        // Output: "March 3, 2026"

        // Number formatting
        final numberFormat = NumberFormat('###,##0.00', 'es_ES');
        final formattedNumber = numberFormat.format(1234567.89);
        // Output: "1.234.567,89"

        // Currency formatting
        final currencyFormat = NumberFormat.currency(locale: 'en_US', symbol: '\$');
        final formattedCurrency = currencyFormat.format(99.99);
        // Output: "$99.99"

        // Percentage formatting
        final percentFormat = NumberFormat.percentPattern('en_US');
        final formattedPercent = percentFormat.format(0.85);
        // Output: "85%"

        // Compact number formatting
        final compactFormat = NumberFormat.compactCurrency(
            locale: 'en_US',
            symbol: '\$',
        );
        final compactNumber = compactFormat.format(1000000);
        // Output: "$1M"
    }
}
```

---

## RTL Layout Support

### iOS RTL Layout

```swift
// ContentView.swift - SwiftUI
struct RTLAwareLayout: View {
    var body: some View {
        HStack(spacing: 16) {
            Image(systemName: "chevron.left")  // Auto-flips for RTL
            VStack(alignment: .leading) {
                Text("Title").font(.headline)
                Text("Subtitle").font(.subheadline)
            }
            Spacer()
        }
        .environment(\.layoutDirection, .rightToLeft)  // Force RTL
    }
}

// Check if current language is RTL
var isRTL: Bool {
    let currentLanguage = NSLocale.preferredLanguages[0]
    let rtlLanguages = ["ar", "he", "ur", "fa"]
    let languageCode = currentLanguage.split(separator: "-")[0]
    return rtlLanguages.contains(String(languageCode))
}
```

### Android RTL Layout

```xml
<!-- activity_main.xml -->
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="horizontal"
    android:layoutDirection="locale">

    <ImageButton
        android:id="@+id/back_button"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:src="@drawable/ic_back"
        android:contentDescription="@string/back_button" />

    <LinearLayout
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_weight="1"
        android:orientation="vertical"
        android:layout_marginStart="16dp"
        android:layout_marginEnd="16dp">

        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="@string/title"
            android:textAlignment="viewStart" />

    </LinearLayout>
</LinearLayout>

<!-- drawable/ic_back.xml -->
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:autoMirrored="true"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path android:fillColor="@color/primary" android:pathData="M20,11H7.83L13.42,5.41L12,4L4,12l8,8 1.41,-1.41L7.83,13H20v-2z"/>
</vector>
```

### React Native RTL Support

```javascript
import { I18nManager } from 'react-native';
import { useTranslation } from 'react-i18next';

function RTLComponent() {
    const { i18n } = useTranslation();
    const isRTL = I18nManager.isRTL;

    const rtlLanguages = ['ar', 'he', 'ur', 'fa'];
    const shouldForceRTL = rtlLanguages.includes(i18n.language);

    if (shouldForceRTL && !isRTL) {
        I18nManager.forceRTL(true);
        // Restart app to apply changes
    }

    return (
        <View style={[
            styles.container,
            { flexDirection: isRTL ? 'row-reverse' : 'row' }
        ]}>
            <Image source={require('./icon.png')} />
            <Text>{i18n.t('welcome_message')}</Text>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        padding: 16,
        alignItems: 'center',
    },
});
```

### Flutter RTL Support

```dart
// Configure RTL in MaterialApp
MaterialApp(
    localizationsDelegates: [
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
    ],
    supportedLocales: [
        Locale('en'),
        Locale('ar'),
        Locale('he'),
    ],
    builder: (context, child) {
        return Directionality(
            textDirection: isRTL(context) ? TextDirection.rtl : TextDirection.ltr,
            child: child!,
        );
    },
)

// Helper function to determine RTL
bool isRTL(BuildContext context) {
    final locale = Localizations.localeOf(context);
    final rtlLanguages = ['ar', 'he', 'ur', 'fa'];
    return rtlLanguages.contains(locale.languageCode);
}

// RTL-aware layout
class RTLAwareLayout extends StatelessWidget {
    @override
    Widget build(BuildContext context) {
        final isRTL = isRTL(context);

        return Row(
            textDirection: isRTL ? TextDirection.rtl : TextDirection.ltr,
            children: [
                Icon(Icons.arrow_back_ios),  // Auto-mirrors
                SizedBox(width: 16),
                Expanded(
                    child: Column(
                        crossAxisAlignment: isRTL
                            ? CrossAxisAlignment.end
                            : CrossAxisAlignment.start,
                        children: [
                            Text('Title'),
                            Text('Subtitle'),
                        ],
                    ),
                ),
            ],
        );
    }
}
```

---

## Locale-Aware Formatting

### Date Formatting Across Platforms

```swift
// iOS
let date = Date()
let formatter = DateFormatter()
formatter.locale = Locale.current
formatter.dateFormat = "MMMM d, yyyy"  // Locale-aware
let formatted = formatter.string(from: date)

// ISO 8601 format with locale
let iso8601Formatter = ISO8601DateFormatter()
let isoString = iso8601Formatter.string(from: date)
```

```kotlin
// Android
val date = Calendar.getInstance().time
val sdf = SimpleDateFormat("MMMM d, yyyy", Locale.getDefault())
val formatted = sdf.format(date)

// Using Java Time (API 26+)
val formatter = java.time.format.DateTimeFormatter.ofPattern(
    "MMMM d, yyyy",
    Locale.getDefault()
)
val formatted = formatter.format(LocalDate.now())
```

```javascript
// React Native / JavaScript
const date = new Date();
const formatter = new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
});
const formatted = formatter.format(date);
// Output: "March 3, 2026"

const germanFormatter = new Intl.DateTimeFormat('de-DE', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
});
// Output: "3. März 2026"
```

```dart
// Flutter
import 'package:intl/intl.dart';

final date = DateTime.now();
final formatter = DateFormat('MMMM d, yyyy', 'en_US');
final formatted = formatter.format(date);
// Output: "March 3, 2026"

final germanFormatter = DateFormat('d. MMMM yyyy', 'de_DE');
// Output: "3. März 2026"
```

### Number and Currency Formatting

```swift
// iOS - Currency
let currencyFormatter = NumberFormatter()
currencyFormatter.locale = Locale.current
currencyFormatter.numberStyle = .currency
let formatted = currencyFormatter.string(from: NSNumber(value: 99.99))
// en-US: "$99.99", de-DE: "99,99 €"
```

```kotlin
// Android - Currency
val currencyFormatter = NumberFormat.getCurrencyInstance(Locale.getDefault())
val formatted = currencyFormatter.format(99.99)
```

```javascript
// React Native - Currency with Intl
const amount = 99.99;
const usdFormatter = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
});
const eurFormatter = new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency: 'EUR'
});
console.log(usdFormatter.format(amount));  // "$99.99"
console.log(eurFormatter.format(amount));  // "99,99 €"
```

```dart
// Flutter - Currency
import 'package:intl/intl.dart';

final usdFormatter = NumberFormat.currency(locale: 'en_US', symbol: '\$');
final eurFormatter = NumberFormat.currency(locale: 'de_DE', symbol: '€');

print(usdFormatter.format(99.99));  // "$99.99"
print(eurFormatter.format(99.99));  // "99,99 €"
```

---

## Dynamic Language Switching

### iOS Implementation

```swift
// LanguageManager.swift
class LanguageManager: ObservableObject {
    @Published var currentLanguage: String = "en" {
        didSet {
            UserDefaults.standard.set(currentLanguage, forKey: "SelectedLanguage")
            Bundle.setLanguage(currentLanguage)
            NotificationCenter.default.post(name: NSNotification.Name("LanguageDidChange"), object: nil)
        }
    }

    init() {
        self.currentLanguage = UserDefaults.standard.string(forKey: "SelectedLanguage") ?? "en"
    }
}

// Bundle+Language.swift
extension Bundle {
    private static var language: String?

    static func setLanguage(_ language: String) {
        Bundle.language = language
    }

    override open var localizedString(forKey: String, value: String?, table tableName: String?) -> String {
        guard let language = Bundle.language else {
            return super.localizedString(forKey: forKey, value: value, table: tableName)
        }

        let path = Bundle.main.path(forResource: language, ofType: "lproj")
        guard let path = path else {
            return super.localizedString(forKey: forKey, value: value, table: tableName)
        }

        let bundle = Bundle(path: path) ?? self
        return bundle.localizedString(forKey: forKey, value: value, table: tableName)
    }
}

// Usage in SwiftUI
@StateObject var languageManager = LanguageManager()

var body: some View {
    VStack {
        Text(NSLocalizedString("hello_world", comment: ""))

        Picker("Select Language", selection: $languageManager.currentLanguage) {
            Text("English").tag("en")
            Text("Español").tag("es")
            Text("Français").tag("fr")
        }
    }
    .onReceive(NotificationCenter.default.publisher(for: NSNotification.Name("LanguageDidChange"))) { _ in
        // Refresh UI
    }
}
```

### Android Implementation

```kotlin
// LanguageManager.kt
object LanguageManager {
    var currentLanguage: String = "en"
        set(value) {
            field = value
            SharedPreferences.Editor().putString("selectedLanguage", value).apply()
            setAppLanguage(value)
        }

    fun setAppLanguage(languageCode: String) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            val locales = LocaleList(Locale(languageCode))
            AppCompatDelegate.setApplicationLocales(locales)
        }
    }

    fun initFromPreferences(context: Context) {
        val saved = SharedPreferences.getString("selectedLanguage", "en")
        currentLanguage = saved
    }
}

// Activity Implementation
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        LanguageManager.initFromPreferences(this)
        setContentView(R.layout.activity_main)
    }
}
```

### React Native Implementation

```javascript
// LanguageContext.js
import React, { createContext, useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import AsyncStorage from '@react-native-async-storage/async-storage';

export const LanguageContext = createContext();

export function LanguageProvider({ children }) {
    const { i18n } = useTranslation();
    const [currentLanguage, setCurrentLanguage] = useState('en');

    useEffect(() => {
        loadSavedLanguage();
    }, []);

    const loadSavedLanguage = async () => {
        const saved = await AsyncStorage.getItem('selectedLanguage');
        if (saved) {
            setCurrentLanguage(saved);
            await i18n.changeLanguage(saved);
        }
    };

    const changeLanguage = async (languageCode) => {
        setCurrentLanguage(languageCode);
        await i18n.changeLanguage(languageCode);
        await AsyncStorage.setItem('selectedLanguage', languageCode);
    };

    return (
        <LanguageContext.Provider value={{ currentLanguage, changeLanguage }}>
            {children}
        </LanguageContext.Provider>
    );
}

// Usage in Components
function SettingsScreen() {
    const { currentLanguage, changeLanguage } = useContext(LanguageContext);
    const { t } = useTranslation();

    return (
        <View>
            <Picker
                selectedValue={currentLanguage}
                onValueChange={changeLanguage}
            >
                <Picker.Item label={t('english')} value="en" />
                <Picker.Item label={t('spanish')} value="es" />
                <Picker.Item label={t('french')} value="fr" />
            </Picker>
        </View>
    );
}
```

### Flutter Implementation

```dart
// language_provider.dart
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class LanguageProvider extends ChangeNotifier {
    Locale _locale = Locale('en');

    Locale get locale => _locale;

    LanguageProvider() {
        _loadSavedLanguage();
    }

    Future<void> _loadSavedLanguage() async {
        final prefs = await SharedPreferences.getInstance();
        final savedLanguage = prefs.getString('selectedLanguage') ?? 'en';
        _locale = Locale(savedLanguage);
        notifyListeners();
    }

    Future<void> setLanguage(String languageCode) async {
        _locale = Locale(languageCode);
        notifyListeners();

        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('selectedLanguage', languageCode);
    }
}

// main.dart
void main() {
    runApp(
        ChangeNotifierProvider(
            create: (_) => LanguageProvider(),
            child: MyApp(),
        ),
    );
}

class MyApp extends StatelessWidget {
    @override
    Widget build(BuildContext context) {
        return Consumer<LanguageProvider>(
            builder: (context, languageProvider, _) {
                return MaterialApp(
                    locale: languageProvider.locale,
                    supportedLocales: [
                        Locale('en'),
                        Locale('es'),
                        Locale('fr'),
                    ],
                    home: SettingsScreen(),
                );
            },
        );
    }
}

// SettingsScreen
class SettingsScreen extends StatelessWidget {
    @override
    Widget build(BuildContext context) {
        return Consumer<LanguageProvider>(
            builder: (context, languageProvider, _) {
                return Scaffold(
                    appBar: AppBar(title: Text(S.of(context).settings_title)),
                    body: ListView(
                        children: [
                            ListTile(
                                title: Text('English'),
                                onTap: () => languageProvider.setLanguage('en'),
                            ),
                            ListTile(
                                title: Text('Español'),
                                onTap: () => languageProvider.setLanguage('es'),
                            ),
                        ],
                    ),
                );
            },
        );
    }
}
```

---

## Translation Management Platforms

### Crowdin Integration

```bash
# Installation
npm install @crowdin/crowdin-api-client

# Configuration
crowdin config set api-token YOUR_API_TOKEN
crowdin config set base-path /path/to/project
crowdin config set project-id 123456
```

```json
// crowdin.yaml
project_id: 123456
api_token: ${CROWDIN_TOKEN}

files:
  - source: /locales/en.json
    translation: /locales/%locale_with_underscore%.json
    languages_mapping:
      es: es-ES
      fr: fr-FR
      ja: ja-JP
  - source: /android/app/src/main/res/values/strings.xml
    translation: /android/app/src/main/res/values-%android_code%/strings.xml
  - source: /ios/Localizable.strings
    translation: /ios/%locale%.lproj/Localizable.strings
```

```javascript
// scripts/crowdin-sync.js
const crowdin = require('@crowdin/crowdin-api-client');

const api = new crowdin.default({
    token: process.env.CROWDIN_TOKEN,
});

async function syncTranslations() {
    try {
        // Download translations
        const translations = await api.translationsApi.listProjectTranslations(
            process.env.PROJECT_ID
        );

        console.log('Downloaded translations:', translations);
    } catch (error) {
        console.error('Sync failed:', error);
    }
}

syncTranslations();
```

### Lokalise Integration

```bash
# Installation
npm install @lokalise/node-sdk

# CLI
npx lokalise2 --token YOUR_API_TOKEN --project-id YOUR_PROJECT_ID
```

```javascript
// scripts/lokalise-sync.js
const LokaliseApi = require('@lokalise/node-sdk');

const lokalise = new LokaliseApi({
    apiToken: process.env.LOKALISE_TOKEN,
});

async function downloadTranslations() {
    try {
        const bundle = await lokalise.files.download(
            process.env.PROJECT_ID,
            {
                format: 'json',
                indentation: '2sp',
                plural_format: 'json',
                include_comments: true,
            }
        );

        console.log('Bundle URL:', bundle.bundle_url);
    } catch (error) {
        console.error('Download failed:', error);
    }
}

downloadTranslations();
```

### Phrase Integration

```bash
# Installation
npm install @phrase/sdk

# Configuration
phrase init
```

```javascript
// scripts/phrase-sync.js
const PhraseApp = require('@phrase/sdk');

const client = new PhraseApp.default({
    apiToken: process.env.PHRASE_TOKEN,
});

async function uploadSourceStrings() {
    try {
        await client.locales.create(
            process.env.PROJECT_ID,
            {
                name: 'English',
                code: 'en',
            }
        );

        console.log('Source strings uploaded');
    } catch (error) {
        console.error('Upload failed:', error);
    }
}

uploadSourceStrings();
```

---

## Pseudo-Localization

### Testing with Pseudo-Localization

Pseudo-localization helps identify untranslated strings and layout issues before real translations arrive.

```javascript
// utils/pseudoLocalization.js
export function toPseudoLocale(text) {
    const expansionMap = {
        a: 'å', e: 'ë', i: 'î', o: 'ô', u: 'û',
        A: 'Å', E: 'Ë', I: 'Î', O: 'Ô', U: 'Û',
    };

    let pseudo = '';
    for (let char of text) {
        pseudo += expansionMap[char] || char;
    }

    // Add visual markers
    return `[${pseudo}]`;
}

// i18n/config.js - Pseudo-locale option
const i18n = {
    ...config,
    resources: {
        ...resources,
        'pseudo': {
            translation: new Proxy(resources.en.translation, {
                get(target, prop) {
                    const value = target[prop];
                    if (typeof value === 'string') {
                        return toPseudoLocale(value);
                    }
                    return value;
                },
            }),
        },
    },
};
```

```dart
// Flutter pseudo-localization
String toPseudoLocale(String text) {
    const expansionMap = {
        'a': 'å', 'e': 'ë', 'i': 'î', 'o': 'ô', 'u': 'û',
        'A': 'Å', 'E': 'Ë', 'I': 'Î', 'O': 'Ô', 'U': 'Û',
    };

    String pseudo = '';
    for (int i = 0; i < text.length; i++) {
        String char = text[i];
        pseudo += expansionMap[char] ?? char;
    }

    return '[$pseudo]';
}
```

---

## App Store Metadata Localization

### iOS App Store Metadata

```swift
// Store metadata in localization files
// en.lproj/InfoPlist.strings
"CFBundleDisplayName" = "MyApp";
"NSAppTransportSecurityDescription" = "App requires internet access";

// es.lproj/InfoPlist.strings
"CFBundleDisplayName" = "MiAplicación";
"NSAppTransportSecurityDescription" = "La aplicación requiere acceso a internet";

// App Store Connect metadata
// Create Localizable.strings in project:
"app_subtitle" = "Stay connected";
"app_description" = "Your best communication app";
"app_keywords" = "chat, messaging, social";
"release_notes" = "Bug fixes and performance improvements";
```

### Android Play Store Metadata

```xml
<!-- fastlane/metadata/android/en-US/short_description.txt -->
MyApp - Stay connected with friends

<!-- fastlane/metadata/android/en-US/full_description.txt -->
MyApp is your best communication platform. Connect with friends and family instantly.

Features:
- Real-time messaging
- Voice calls
- Video calls
- Group chats

<!-- fastlane/metadata/android/en-US/title.txt -->
MyApp - Messaging & Chat

<!-- fastlane/metadata/android/es-ES/short_description.txt -->
MiAplicación - Mantente conectado con amigos

<!-- fastlane/metadata/android/es-ES/full_description.txt -->
MiAplicación es tu mejor plataforma de comunicación. Conéctate con amigos y familia al instante.

Características:
- Mensajería en tiempo real
- Llamadas de voz
- Videollamadas
- Chats grupales
```

### Fastlane for App Store Localization

```ruby
# fastlane/Fastfile
default_platform(:ios)

platform :ios do
    desc "Upload localized metadata to App Store"
    lane :upload_metadata do
        deliver(
            username: ENV['APPLE_ID'],
            app_identifier: "com.yourcompany.myapp",
            submit_for_review: false,
            automatic_release: false,
            force: true,
            skip_screenshots: true,
            metadata_path: "fastlane/metadata",
            precheck_include_in_app_purchases: false
        )
    end
end

platform :android do
    desc "Upload localized metadata to Google Play"
    lane :upload_play_store_metadata do
        supply(
            package_name: "com.yourcompany.myapp",
            json_key_data: ENV['GOOGLE_PLAY_KEY'],
            metadata_path: "fastlane/metadata/android",
            skip_upload_apk: true,
            skip_upload_aab: true
        )
    end
end
```

---

## Cultural Considerations

### Icons and Graphics

```swift
// iOS - Context-aware icons
let iconName = Locale.current.languageCode == "ar" ? "icon-mirrored" : "icon"
Image(iconName)

// Right-to-left specific icons
if Locale.current.languageCode == "ar" || Locale.current.languageCode == "he" {
    Image("icon-mirrored")
} else {
    Image("icon")
}
```

```kotlin
// Android - Language-specific drawables
// res/drawable-en/ic_arrow.xml
// res/drawable-ar/ic_arrow.xml (mirrored)

// Usage
val drawableId = if (isRTL) R.drawable.ic_arrow_rtl else R.drawable.ic_arrow
```

```javascript
// React Native - Culture-aware content
const culturalSettings = {
    'en': { colors: ['#FF0000', '#00FF00'], weekStart: 0 },
    'ar': { colors: ['#00FF00', '#FF0000'], weekStart: 6 },
    'ja': { colors: ['#FF0000', '#FFFFFF'], currency: '¥' },
};

const currentCulture = culturalSettings[i18n.language] || culturalSettings.en;
```

### Date and Time Conventions

```swift
// iOS - Respect locale date conventions
let dateFormatter = DateFormatter()
dateFormatter.locale = Locale.current
dateFormatter.dateStyle = .medium
dateFormatter.timeStyle = .short

// Different formats automatically applied:
// en-US: "Mar 3, 2026, 2:30 PM"
// de-DE: "03.03.2026, 14:30"
// ja-JP: "2026年3月3日 14:30"
```

```dart
// Flutter - Date conventions
import 'package:intl/date_symbol_data_local.dart';

void main() {
    initializeDateFormatting();  // Initialize locale data
    runApp(MyApp());
}

// Use DateFormat with locale awareness
final format = DateFormat.yMMMd(Locale.current.toString());
```

### Name and Address Formatting

```swift
// iOS - Proper name formatting
let formatter = PersonNameComponentsFormatter()
let components = PersonNameComponents()
components.givenName = "John"
components.familyName = "Smith"

let formatted = formatter.string(from: components)
// Output varies by locale
```

```kotlin
// Android - Address formatting
val formatter = AddressFormatter()
val address = Address(
    street = "123 Main St",
    city = "San Francisco",
    state = "CA",
    zipCode = "94102",
    country = "United States"
)

val formatted = formatter.format(address, Locale.getDefault())
```

### Numeric Conventions

```javascript
// Different numeric formats by locale
const number = 1234567.89;

// US format: 1,234,567.89
const usFormat = new Intl.NumberFormat('en-US').format(number);

// German format: 1.234.567,89
const deFormat = new Intl.NumberFormat('de-DE').format(number);

// French format: 1 234 567,89
const frFormat = new Intl.NumberFormat('fr-FR').format(number);
```

### Color and Symbolism

```dart
// Flutter - Culture-aware color schemes
final colorMap = {
    'en': Colors.blue,    // Trusted blue
    'zh': Colors.red,     // Luck and prosperity
    'ar': Colors.green,   // Nature and life
    'in': Colors.orange,  // Saffron
};

final culturalColor = colorMap[Locale.current.languageCode] ?? Colors.blue;
```

---

## Best Practices Summary

1. **Always use locale-aware formatters** - Never hardcode date/number/currency formats
2. **Plan for text expansion** - Some languages expand 30-50% during translation
3. **Provide context to translators** - Use comments and descriptions in string files
4. **Test with pseudo-localization** - Catch layout issues before translations arrive
5. **Support per-app language selection** - Allow users to choose independently of system settings
6. **Handle RTL languages properly** - Use leading/trailing margins and mirrored icons
7. **Use translation management platforms** - Streamline workflow and collaboration
8. **Respect cultural nuances** - Colors, icons, and imagery differ across cultures
9. **Implement dynamic language switching** - Users expect instant language changes
10. **Localize app store metadata** - Increase discoverability in multiple markets
