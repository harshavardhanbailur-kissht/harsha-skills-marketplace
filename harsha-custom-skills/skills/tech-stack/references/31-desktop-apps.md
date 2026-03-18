# Desktop Application Frameworks: 2025-2026 Tech Stack Comparison

## Executive Summary

This document provides a comprehensive technical comparison of leading desktop application frameworks: Electron, Tauri, Wails, Flutter Desktop, and .NET MAUI. Data reflects current versions and features as of February 2026.

**TL;DR Decision Matrix:**
- **Electron**: Mature, massive ecosystem, higher resource costs. Use for complex UIs requiring full Node.js power.
- **Tauri 2.0**: Lightweight, fast, secure. Ideal for resource-conscious apps. 10x smaller bundle than Electron.
- **Wails**: Go-based alternative to Tauri. Best for Go developers.
- **Flutter Desktop**: Modern, unified codebase across mobile/desktop. Still maturing on desktop.
- **.NET MAUI**: Microsoft's cross-platform solution. Desktop support growing with Avalonia expansion.

---

## 1. Framework Comparison Matrix

### Tauri 2.0

| Dimension | Details |
|-----------|---------|
| **Language** | Rust (backend) + Web Stack (frontend) |
| **Version** | 2.0 (Stable, released late 2024) |
| **Bundle Size (Hello World)** | 2.5-10 MB (typically under 10 MB) |
| **Memory Usage (Idle)** | 30-40 MB |
| **Startup Time** | <500 ms |
| **Native API Access** | Via Rust bridge; permission-based security model |
| **Cross-Platform Support** | Windows, macOS, Linux |
| **Web Tech Reuse** | React, Vue, Svelte, Angular - full support |
| **Auto-Update Mechanism** | Built-in updater plugin with configurable endpoints |
| **Code Signing & Distribution** | Platform-native signing; distributes via direct download or custom servers |
| **App Store Support** | Limited (no direct Mac App Store or Windows Store integration) |

**Key Tauri 2.0 Features:**
- File associations support in bundler
- Async URI scheme protocol handler (`register_asynchronous_uri_scheme_protocol`)
- Enhanced drag-and-drop with positional events
- Improved Linux, macOS, and Windows platform support
- 35% YoY adoption growth (late 2024)
- Security-first: all dangerous APIs blocked by default

**Advantages:**
- Extremely lightweight and fast
- Superior security model through Rust
- Single-digit MB installers
- Native system WebView integration
- Fast development iteration

**Disadvantages:**
- Smaller ecosystem than Electron
- Rust learning curve for backend development
- Limited third-party library ecosystem
- No direct app store integration

---

### Electron

| Dimension | Details |
|-----------|---------|
| **Language** | JavaScript/TypeScript + Node.js |
| **Latest Version** | Multiple major versions tied to Chromium releases |
| **Bundle Size (Hello World)** | 100-300 MB (typical apps) |
| **Memory Usage (Idle)** | 200-300 MB |
| **Startup Time** | 1-2 seconds |
| **Native API Access** | Node.js ecosystem; direct OS access via native modules |
| **Cross-Platform Support** | Windows, macOS, Linux |
| **Web Tech Reuse** | Full-featured; embedded Chromium |
| **Auto-Update Mechanism** | Multiple solutions (electron-builder, Electron Forge) |
| **Code Signing & Distribution** | Mature; supports code signing and notarization |
| **App Store Support** | Mac App Store (macOS), limited Windows Store |

**Auto-Update & Code Signing (2025-2026):**
- **macOS**: Requires code signing for auto-updates via Squirrel.Mac
- **Windows**: Supported via electron-builder and Electron Forge
- **Linux**: No built-in auto-update support
- Code signature validation available on macOS and Windows
- Cloud-based signing (Azure Trusted Signing) now available for US/Canada organizations
- Support for GitHub Releases, S3, DigitalOcean Spaces, Keygen, and generic HTTPS

**Advantages:**
- Massive mature ecosystem
- Proven at scale (Slack, Discord, VS Code, etc.)
- Full Chromium rendering consistency
- Extensive Node.js module support
- Mature documentation and tooling

**Disadvantages:**
- Heavy resource consumption (100-300+ MB per install)
- Slow startup times (1-2 seconds)
- High memory footprint
- Bundled Chromium increases binary size
- Overkill for simple applications

**When Electron is Still the Right Choice:**
- Apps requiring advanced browser APIs or cutting-edge web features
- Heavy Node.js dependencies (scientific computing, file processing)
- Complex multi-window workflows at scale
- Team already invested in JavaScript ecosystem
- Rapid iteration needed and ecosystem matters more than resources
- App UI complexity justifies resource cost

---

### Wails

| Dimension | Details |
|-----------|---------|
| **Language** | Go (backend) + Web Stack (frontend) |
| **Version** | Stable with active development |
| **Bundle Size (Hello World)** | Smaller than Electron; typically 5-15 MB range |
| **Memory Usage (Idle)** | 20-50 MB (comparable to Tauri) |
| **Startup Time** | <500 ms |
| **Native API Access** | Go APIs exposed to JavaScript via automatic bindings |
| **Cross-Platform Support** | Windows, macOS, Linux |
| **Web Tech Reuse** | React, Vue, Svelte fully supported |
| **Auto-Update Mechanism** | Community implementations (not built-in) |
| **Code Signing & Distribution** | Manual platform-specific signing required |
| **App Store Support** | Manual process; not streamlined |

**Key Wails Features:**
- Automatic Go-to-JavaScript method exposure
- Auto-generated TypeScript models from Go structs
- Any frontend framework support
- Built-in CLI for generation, building, bundling
- No Chromium embedding overhead
- Fast build times

**Advantages:**
- Excellent for Go developers
- Lightweight and fast (comparable to Tauri)
- Flexible frontend options
- Native interop without overhead
- Strong CLI tooling

**Disadvantages:**
- Smaller community than Electron/Tauri
- No built-in auto-update mechanism
- Fewer third-party integrations
- Less mature ecosystem
- Go backend learning curve for non-Go teams

**Best For:**
- Go developers wanting to build desktop apps
- Backend systems needing a lightweight UI
- Tools and utilities where Go excels
- Cross-platform CLI applications

---

### Flutter Desktop

| Dimension | Details |
|-----------|---------|
| **Language** | Dart |
| **Version** | Stable; advancing toward 4.0 (2026) |
| **Bundle Size (Hello World)** | 50-150 MB (varies by optimization) |
| **Memory Usage** | 60-120 MB (platform dependent) |
| **Startup Time** | 500-1000 ms |
| **Native API Access** | Improved; direct native interop in development |
| **Cross-Platform Support** | Windows, macOS, Linux, iOS, Android, Web |
| **Web Tech Reuse** | Uses Skia rendering; not traditional web stack |
| **Auto-Update Mechanism** | Community solutions; evolving |
| **Code Signing & Distribution** | Platform-specific signing required |
| **App Store Support** | Planned improvements for 2026 |

**Flutter 2025-2026 Desktop Enhancements:**
- **Direct Native Interop**: New initiative for seamless native API access
- **Thread Merge**: Completed for Android/iOS; rolling out to Windows/macOS
- **Build Hooks**: Support for bundling native code with Dart packages (preview)
- **FFIgen & JNIgen**: Codegen tools for simplified native API bridging
- **Desktop APIs**: Windowing, menus, native dialogs as standard
- **Impeller Optimizations**: Next-phase graphics pipeline improvements
- **Material Design 3**: Enhanced integration across platforms
- **App Size Reduction**: Via modularization and core module refinement

**Advantages:**
- Single codebase for mobile + desktop + web
- Modern UI framework with excellent developer experience
- Hot reload for rapid iteration
- Growing desktop support
- Consistent rendering across platforms
- Strong Google backing

**Disadvantages:**
- Desktop still maturing compared to mobile
- Larger bundle sizes than Electron/Tauri
- Dart ecosystem smaller than JavaScript/Go
- Traditional web tech reuse limited
- Still evolving auto-update and app store integration

**Best For:**
- Teams building mobile-first apps needing desktop companion
- Startups prioritizing code reuse across platforms
- Applications where Material Design is appropriate
- Teams comfortable with Dart ecosystem

---

### .NET MAUI

| Dimension | Details |
|-----------|---------|
| **Language** | C# / .NET |
| **Version** | .NET 10 (current); targeting .NET 11 |
| **Bundle Size (Hello World)** | 50-200 MB (platform dependent) |
| **Memory Usage** | 80-150 MB |
| **Startup Time** | 1-2 seconds |
| **Native API Access** | Platform-native APIs; improving interop |
| **Cross-Platform Support** | Windows, macOS, iOS, Android (Linux/Web via Avalonia, 2026) |
| **Web Tech Reuse** | Limited; uses XAML for UI definition |
| **Auto-Update Mechanism** | Platform-specific solutions |
| **Code Signing & Distribution** | Platform-specific; mature for Windows/macOS |
| **App Store Support** | Windows Store, Mac App Store (via signed packages) |

**2025-2026 MAUI Expansion:**
- **Avalonia Backend Integration**: Linux and browser support planned via Avalonia renderer
- **Status**: WebAssembly sample online; preview access signup for Q1 2026
- **Single Codebase Goal**: Develop once, deploy to Android, iOS, macOS, Windows, Linux, Web
- **Modernization**: Leveraging latest .NET 10/11 improvements

**Advantages:**
- Single codebase for mobile and desktop
- Strong Microsoft ecosystem support
- Native performance on supported platforms
- XAML for declarative UI
- Growing platform support

**Disadvantages:**
- Linux/Web support not yet production-ready
- Larger bundle sizes than Tauri/Wails
- Less cross-platform parity than Flutter
- C# not as widespread as JavaScript
- Slower startup than lightweight frameworks

**Best For:**
- Microsoft-ecosystem-aligned teams
- Enterprise Windows/macOS applications
- Teams leveraging existing C# infrastructure
- Applications needing tight OS integration

---

## 2. Tauri vs Electron: Deep Dive Comparison

### Performance Metrics (2025-2026)

| Metric | Tauri 2.0 | Electron | Winner |
|--------|-----------|----------|--------|
| **Bundle Size** | 2.5-10 MB | 100-300 MB | Tauri (~30x smaller) |
| **Installed Size** | 10-50 MB | 200-600 MB | Tauri (10-100x difference) |
| **Memory (Idle)** | 30-40 MB | 200-300 MB | Tauri (~7x less) |
| **Startup Time** | <500 ms | 1-2 seconds | Tauri (~2-4x faster) |
| **Binary Overhead** | Minimal | Large (Chromium) | Tauri |

**Important Context (2025):** While metrics heavily favor Tauri, some benchmarks show negligible differences when both use platform WebView (Edge 2 on Windows), suggesting Chromium overhead itself is the primary differentiator.

### Architecture Differences

**Tauri:**
- Rust core process
- Platform system WebView (Safari/WebKit on macOS, WebView2 on Windows, GTK WebKit on Linux)
- Lightweight IPC bridge
- Security-first permission model
- No bundled browser engine

**Electron:**
- Node.js main process
- Embedded Chromium rendering engine
- Full Node.js standard library access
- Broader API surface
- Consistent cross-platform rendering

### Security Model Comparison

**Tauri 2.0:**
- Permission-based architecture: all dangerous APIs blocked by default
- Explicit capabilities configuration required per API
- Rust type safety prevents entire classes of bugs
- Minimal attack surface through API bridge
- Security audit trail via permissions config
- Each plugin requires explicit scoping

**Electron:**
- Less restrictive by default
- Full Node.js access available in main process
- IPC channels can expose broad APIs
- Preload scripts increase attack surface
- More responsibility on developer to secure

### When Electron Still Wins (2025-2026)

1. **Advanced Browser APIs**: WebGL 2, Web Workers, complex Canvas operations
2. **Node.js Dependencies**: Scientific computing, video processing, database drivers unavailable in Rust/Go
3. **Legacy Code**: Existing codebase investing in Node.js tooling
4. **Team Expertise**: JavaScript developers outnumber Rust developers
5. **Rapid Prototyping**: Massive library ecosystem accelerates development
6. **Complex IPC Patterns**: Multi-window apps with heavy inter-process communication
7. **Enterprise Integration**: Extensive Node.js backend infrastructure
8. **Platform-Specific Features**: Edge cases requiring Electron's Chromium version
9. **Developer Productivity**: For teams already JavaScript-heavy

---

## 3. Native API Access Comparison

### Tauri 2.0 Native APIs

**Available Plugins (Core):**
- File System (with permission scoping)
- Opener (open files/URLs)
- Updater
- Notification
- Clipboard
- Window management
- System tray
- Dialog (file/folder/save)
- Process spawning
- HTTP client
- Shell operations

**Permission System:**
- Core permissions (allow/deny by default)
- Plugin-level fine-grained control
- Capability-based security
- Scope-based scoping (e.g., which directories readable)
- No root access without explicit permission

**Development Flow:**
```
Request API → Permission blocked by default → Enable in capabilities.json → Declare allowlist → Use in code
```

### Electron Native APIs

**Access Methods:**
1. Node.js native modules (require thousands available)
2. Native C++ bindings via native-module
3. Direct OS calls via FFI or ctypes
4. Platform-specific code (ipcMain handlers)

**Popular Modules:**
- file-system operations (fs, path, etc.)
- system (os, process, child_process)
- hardware (hardware-related packages)
- platform-specific APIs via binding generators

**Advantages:**
- Unlimited native access via Node.js
- Massive module ecosystem
- Direct system integration
- Third-party library support

### Wails Native APIs

**Go Interop:**
- Automatic method exposure to frontend
- Go standard library available
- Native bindings via cgo
- External package integration
- TypeScript stub generation for frontend

**Limitations:**
- No auto-update built-in
- Community-driven plugin ecosystem
- Manual platform-specific code integration

---

## 4. Cross-Platform Support Details

### Tauri 2.0
- **Windows**: Full support (WebView2 backend)
- **macOS**: Full support (WKWebView backend)
- **Linux**: Full support (GTK WebKit backend)
- **Status**: Stable production-ready

### Electron
- **Windows**: Full support
- **macOS**: Full support (with notarization for distribution)
- **Linux**: Full support (multiple distro support)
- **Status**: Mature, proven at scale

### Wails
- **Windows**: Full support
- **macOS**: Full support
- **Linux**: Full support
- **Status**: Stable; active development

### Flutter Desktop
- **Windows**: Stable
- **macOS**: Stable
- **Linux**: Stable
- **iOS**: Stable (mobile)
- **Android**: Stable (mobile)
- **Web**: Improving
- **Status**: Desktop maturing

### .NET MAUI
- **Windows**: Full support
- **macOS**: Full support
- **iOS**: Full support
- **Android**: Full support
- **Linux**: Coming 2026 via Avalonia
- **Web**: Coming 2026 via Avalonia (preview Q1)
- **Status**: Expanding platforms

---

## 5. Auto-Update Mechanisms (2025-2026)

### Tauri 2.0
**Built-in Updater Plugin:**
- Configuration-driven endpoint setup
- Delta updates supported
- Signature verification
- Rust and JavaScript API access
- Cross-platform (Windows, macOS, Linux)
- Some APIs restricted to Rust for security

**Configuration Example:**
```toml
[tauri.bundle.updater]
active = true
endpoints = ["https://updates.myapp.com/{{target}}/{{current_version}}"]
dialog = true
pubkey = "..." # public key for verification
```

### Electron
**macOS & Windows (No Linux):**
- **electron-builder**: Supports GitHub Releases, S3, DigitalOcean, Keygen, HTTPS
- **electron-updater**: Simplified API for auto-updates
- **electron-notarize**: macOS notarization integration
- Squirrel.Mac requires code signing
- Delta updates available

**Configuration:**
```json
{
  "publish": [
    {
      "provider": "github",
      "owner": "...",
      "repo": "..."
    }
  ]
}
```

**2025-2026 Update:**
- Cloud-based signing (Azure Trusted Signing) now available
- Streamlined CI/CD integration
- Notarization automation improved

### Wails
**No Built-in:**
- Community solutions required
- Must implement custom update logic
- Platform-specific handling needed

### Flutter
**Evolving:**
- Platform-specific mechanisms
- Community packages emerging
- Improving as desktop matures

### .NET MAUI
**Platform-Specific:**
- Windows Store automatic updates
- macOS App Store updates
- Manual implementation for direct distribution

---

## 6. Code Signing & Distribution

### Tauri 2.0
**Distribution Methods:**
- Direct download (installers)
- Custom servers
- GitHub Releases
- Self-hosted update servers

**Code Signing:**
- Windows: Optional but recommended (requires Authenticode certificate)
- macOS: Required for App Store; highly recommended for direct distribution
- Linux: Not required but possible with GPG

**Simplicity:** Minimal signing overhead; primarily platform requirements

### Electron
**Distribution Channels:**
- Mac App Store (with MAS certificate)
- Windows Store (limited adoption)
- Direct download with electron-builder
- Custom update servers
- GitHub Releases

**Code Signing & Notarization:**
- **macOS**: Requires 3rd Party Developer Certificate + Apple Distribution Certificate; notarization mandatory for distribution
- **Windows**: Authenticode certificate (optional but recommended)
- **Process**: electron-builder automates most signing steps

**Certificates Required (macOS):**
- 3rd Party Mac Developer Installer
- 3rd Party Mac Developer Application or Apple Distribution

**Cloud Signing (2025):**
- Azure Trusted Signing available for US/Canada orgs
- Removes local key management
- Speeds up CI/CD signing

### Wails
**Requirements:**
- Platform-native certificate setup
- Manual signing for macOS/Windows
- No automation tooling provided
- Installer creation must be manual or via external tools

### Flutter
**Status:**
- Platform-specific signing required
- Tooling improving but not as automated as Electron
- Mac App Store support developing

### .NET MAUI
**App Stores:**
- Windows Store signing automated
- Mac App Store with appropriate certificates
- Direct distribution requires OS-specific signing

---

## 7. App Store Support (February 2026)

### Tauri 2.0
- **Mac App Store**: Not supported (architecture incompatible with sandboxing model)
- **Windows Store**: Not officially supported
- **Linux Stores**: AppImage, Snap, Flatpak support via bundler
- **Verdict**: Direct distribution only; focus on GitHub Releases and custom servers

### Electron
- **Mac App Store**: Supported (MAS build separate from direct download)
- **Windows Store**: Limited support (not primary distribution channel)
- **Official Recommendation**: GitHub Releases + electron-updater for most apps
- **Verdict**: Possible but direct distribution is recommended for most use cases

### Wails
- **Mac App Store**: Possible but requires manual setup
- **Windows Store**: Possible but requires manual setup
- **Verdict**: Not streamlined; direct distribution preferable

### Flutter
- **App Stores**: Improving integration for 2026
- **Status**: Platform support still evolving
- **Verdict**: Use native store distribution where available; web/desktop less mature

### .NET MAUI
- **Mac App Store**: Supported via certificate configuration
- **Windows Store**: Native integration
- **Verdict**: Best story for app store distribution in 2026

---

## 8. Decision Logic & IF/THEN Rules

### Core Decision Tree

```
START: Need a desktop app?
│
├─ Is resource efficiency critical?
│  │
│  ├─ YES + Team knows Rust?
│  │  └─ CHOOSE: Tauri 2.0
│  │     Reason: Best bundle size, memory, startup. Rust type safety.
│  │
│  ├─ YES + Team knows Go?
│  │  └─ CHOOSE: Wails
│  │     Reason: Go simplicity with lightweight desktop app benefits.
│  │
│  └─ NO + Need massive ecosystem?
│     └─ CHOOSE: Electron
│        Reason: Node.js ecosystem worth the resource cost.
│
├─ Is single codebase (mobile + desktop) required?
│  │
│  ├─ YES + Prefer Material Design?
│  │  └─ CHOOSE: Flutter Desktop
│  │     Reason: Single Dart codebase; unified mobile/desktop/web.
│  │
│  └─ YES + Prefer C# / Microsoft ecosystem?
│     └─ CHOOSE: .NET MAUI
│        Reason: Single codebase; Windows/macOS stable; Linux coming 2026.
│
├─ Is security paramount?
│  │
│  ├─ YES + Web tech needed?
│  │  └─ CHOOSE: Tauri 2.0
│  │     Reason: Permission-based security model; Rust type safety.
│  │
│  └─ NO + Need wide Node.js integration?
│     └─ CHOOSE: Electron
│        Reason: Accept security responsibility for ecosystem power.
│
├─ Is app store distribution critical?
│  │
│  ├─ YES + Must support Windows Store + Mac App Store?
│  │  └─ CHOOSE: .NET MAUI (or Electron for MAS fallback)
│  │     Reason: MAUI has native app store integration.
│  │
│  └─ YES + MAS only?
│     └─ CHOOSE: Electron
│        Reason: Proven MAS distribution pipeline.
│
└─ Default (balanced choice)?
   ├─ Team has JavaScript? + Not ultra-resource-constrained?
   │  └─ CHOOSE: Electron
   │     Reason: Mature, proven, ecosystem depth.
   │
   ├─ Team modern + values startup speed?
   │  └─ CHOOSE: Tauri 2.0
   │     Reason: Modern default; meets most needs with less overhead.
   │
   └─ Team polyglot + values simplicity?
      └─ CHOOSE: Flutter Desktop (if mobile also needed)
            OR Tauri (if desktop-only or tight resources)
```

### Specific Scenario Rules

**Scenario 1: Lightweight Utility / System Tool**
```
IF size < 5MB OR memory-constrained device
  THEN Tauri 2.0
  REASON: Installers 10-50MB; idle ~40MB; sub-500ms startup
```

**Scenario 2: Complex Web App to Desktop**
```
IF existing web app + Node.js backend integration required
  THEN Electron
  REASON: Reuse Node.js code; massive library ecosystem
  UNLESS: Can refactor backend to Rust/Go
    THEN Tauri or Wails (gains efficiency benefits)
```

**Scenario 3: Enterprise Cross-Platform Desktop**
```
IF Windows + macOS + Linux ALL required
  AND security critical
  AND lightweight needed
  THEN Tauri 2.0
  REASON: Best all-around for enterprise desktop

IF Windows + macOS only + app store needed
  THEN .NET MAUI (preview) or Electron
  REASON: App store integration more mature
```

**Scenario 4: Startup Building First Product**
```
IF small team + fast iteration critical
  AND unclear platform requirements
  THEN Flutter Desktop
  REASON: Single codebase enables pivoting mobile/desktop/web

IF desktop-only proven need + resources tight
  THEN Tauri 2.0
  REASON: Fast dev cycle; lightweight production build
```

**Scenario 5: High-Performance System Integration**
```
IF deep OS integration required (file system, system tray, hardware)
  AND Node.js ecosystem sufficient
  THEN Electron
  REASON: Native module ecosystem; proven patterns

IF deep OS integration + modern safety desired
  THEN Tauri 2.0
  REASON: Permission-based security; Rust type safety

IF Go backend ideal fit (CLI tool with UI)
  THEN Wails
  REASON: Go excels at systems work
```

**Scenario 6: Video/Image Processing Desktop App**
```
IF GPU compute OR media libraries required
  THEN Electron
  REASON: Node.js bindings for ffmpeg, OpenCV, etc.

IF pure computation + lightweight UI
  THEN Wails (Go science packages)
  OR Tauri (invoke heavy computation to Rust/backend)
```

**Scenario 7: Real-Time Collaboration Tool**
```
IF complex multi-window, real-time sync, heavy IPC
  THEN Electron
  REASON: Proven patterns; Node.js async excels at networking

IF lightweight real-time + low resource requirements
  THEN Tauri 2.0
  REASON: Can handle real-time with Rust backend; efficient memory
```

---

## 9. Framework Selection by Priority

### If Bundle Size is #1 Priority
1. Tauri 2.0 (2.5-10 MB)
2. Wails (5-15 MB estimated)
3. Flutter (50-150 MB)
4. .NET MAUI (50-200 MB)
5. Electron (100-300+ MB)

### If Startup Time is #1 Priority
1. Tauri 2.0 (<500 ms)
2. Wails (<500 ms)
3. Flutter (500-1000 ms)
4. .NET MAUI (1-2 seconds)
5. Electron (1-2 seconds)

### If Ecosystem Maturity is #1 Priority
1. Electron (proven at scale; massive library ecosystem)
2. .NET MAUI (Microsoft backing; mature for Windows/macOS)
3. Flutter (strong Google backing; growing rapidly)
4. Tauri 2.0 (maturing; ecosystem growing 35% YoY)
5. Wails (smaller but stable)

### If Developer Productivity is #1 Priority
1. Electron (JavaScript; massive libraries)
2. Flutter (hot reload; single codebase)
3. .NET MAUI (C# productivity; Visual Studio)
4. Tauri 2.0 (emerging tooling; less friction than Rust)
5. Wails (Go simplicity; less automation)

### If Security is #1 Priority
1. Tauri 2.0 (permission-based; Rust type safety)
2. Wails (Go memory safety; smaller surface area than Node.js)
3. Flutter (managed memory; no raw pointer access)
4. .NET MAUI (managed runtime; type safety)
5. Electron (requires careful architecting; full Node.js access risky)

### If Cross-Platform Support is #1 Priority
1. Flutter (Windows, macOS, Linux, iOS, Android, Web in 2026)
2. .NET MAUI (Windows, macOS, iOS, Android; Linux coming 2026)
3. Tauri 2.0 (Windows, macOS, Linux stable)
4. Electron (Windows, macOS, Linux stable)
5. Wails (Windows, macOS, Linux stable)

### If Lowest Total Cost of Ownership
1. **Tauri 2.0**: Smallest hosting cost; fastest updates; minimal resources
2. **Wails**: Go efficiency; minimal resources
3. **Flutter**: Single codebase amortizes development across platforms
4. **Electron**: Mature tooling reduces support burden despite resource cost
5. **.NET MAUI**: Heavy initial investment; payoff on multi-platform deployment

---

## 10. Technology Stack Recommendations (2026)

### Best Default Choice for Most Teams
**Tauri 2.0** (unless specific needs below apply)

**Reasoning:**
- Sweet spot: 90% of use cases covered
- Lightweight production builds (crucial for distribution)
- Modern security model
- Ecosystem growing rapidly
- Learning curve manageable (Rust less scary than expected)
- Performance adequate for all but extreme cases

### Best for Teams Prioritizing Developer Velocity
**Electron**

**Reasoning:**
- Massive ecosystem = faster feature delivery
- JavaScript ubiquity = easier hiring
- Proven patterns for desktop development
- Resource cost acceptable for many businesses

### Best for Cross-Platform App First Strategy
**Flutter Desktop**

**Reasoning:**
- Single Dart codebase pays dividends across platforms
- Hot reload = rapid iteration
- Material Design = polished default UI
- Desktop story maturing; now viable for production

### Best for Enterprise / System Integration
**Tauri 2.0** with Rust backend

**Reasoning:**
- Rust prevents entire classes of bugs (buffer overflows, use-after-free)
- Permission-based security audit trail
- OS integration via safe wrapper pattern

### Best for Go Developers
**Wails**

**Reasoning:**
- Go backend = leverage existing Go skills
- Lightweight production build
- No Chromium overhead
- Ideal for tools and utilities

### Best for Cloud-Native / Existing C# Infrastructure
**.NET MAUI**

**Reasoning:**
- Unified with Azure/cloud ecosystem
- Windows Store integration mature
- App store distribution story improving 2026
- Leverages existing C# development skills

---

## 11. 2026 Outlook & Recommendations

### Tauri Trajectory
- **Expected**: Continued ecosystem growth; stabilization as go-to lightweight framework
- **2026 Focus**: Plugin ecosystem expansion; performance optimizations; broader adoption
- **Recommendation**: Safe bet for new projects; minimal legacy concerns

### Electron Future
- **Expected**: Continued dominance for resource-permissive use cases
- **2026 Focus**: Performance improvements; Windows Store attempts; eco-focus
- **Recommendation**: Still best for teams with Node.js investment; ecosystem matters more

### Flutter Desktop Evolution
- **Expected**: Desktop parity with mobile by 2027; aggressive roadmap
- **2026 Focus**: Direct native interop (major milestone); app size reduction; store integration
- **Recommendation**: Evaluate for new cross-platform projects; ready for production

### Wails Growth
- **Expected**: Steady adoption among Go developers; ecosystem consolidation
- **2026 Focus**: Auto-update mechanisms; plugin ecosystem maturation
- **Recommendation**: Niche winner for Go-first teams

### .NET MAUI Expansion
- **Expected**: Linux/Web support production-ready by late 2026
- **2026 Focus**: Avalonia backend stabilization; app store integration refinement
- **Recommendation**: Watch for Linux support GA; Windows/macOS already solid

---

## 12. Migration Paths

### From Electron to Tauri
- **Feasibility**: High (same web frontend)
- **Effort**: Medium (Rust backend rewrite)
- **Win**: 10-15x smaller bundle; 7x less memory; sub-500ms startup
- **Challenge**: Rust learning; rebuilding Node.js functionality in Rust

### From Web App to Tauri/Electron/Flutter
- **Feasibility**: High
- **Electron**: Easiest (same JavaScript)
- **Tauri**: Web frontend unchanged; Rust backend for business logic
- **Flutter**: Complete rewrite of frontend (Dart); backend agnostic

### Electron to .NET MAUI (for teams)
- **Feasibility**: Low (fundamentally different tech stacks)
- **Win**: App store integration; managed runtime
- **Challenge**: Requires rewriting both frontend and backend

---

## 13. Benchmarks & Performance Data (2025-2026)

### Memory Usage Comparison (Idle State)
```
Tauri 2.0:       30-40 MB
Wails:           20-50 MB
Flutter:         60-120 MB
.NET MAUI:       80-150 MB
Electron:        200-300 MB
```

### Bundle Size (Hello World)
```
Tauri 2.0:       2.5-10 MB
Wails:           5-15 MB
Flutter:         50-150 MB
.NET MAUI:       50-200 MB
Electron:        100-300+ MB
```

### Startup Time
```
Tauri 2.0:       <500 ms
Wails:           <500 ms
Flutter:         500-1000 ms
.NET MAUI:       1-2 seconds
Electron:        1-2 seconds
```

### Important Caveat
Some Tauri vs Electron benchmarks are context-dependent. When both use the same WebView backend (e.g., WebView2 on Windows), memory usage differences narrow because Chromium overhead is the primary factor. However, Tauri's bundle size advantage persists because it doesn't duplicate WebView binaries.

---

## 14. References & Sources

### Research Sources (February 2026)

**Tauri 2.0:**
- [Tauri 2.0 Stable Release](https://v2.tauri.app/blog/tauri-20/)
- [Tauri vs Electron Comprehensive Comparison](https://www.gethopp.app/blog/tauri-vs-electron)
- [Tauri 2025 Framework Comparison](https://codeology.co.nz/articles/tauri-vs-electron-2025-desktop-development.html)
- [Tauri File System Permissions](https://v2.tauri.app/plugin/file-system/)
- [Tauri Auto-Update Plugin](https://v2.tauri.app/plugin/updater/)

**Electron:**
- [Electron Official Documentation](https://www.electronjs.org/docs/latest/)
- [Electron 2026 Development Guide](https://forasoft.medium.com/electron-desktop-app-development-guide-for-business-in-2026-e75e439fe9d4)
- [electron-builder Auto-Update Guide](https://www.electron.build/auto-update.html)
- [Code Signing Best Practices](https://www.electronjs.org/docs/latest/tutorial/code-signing)

**Wails:**
- [Wails Framework Official Site](https://wails.io/)
- [Wails GitHub Repository](https://github.com/wailsapp/wails)
- [Cross-Platform Desktop with Go and Wails](https://talent500.com/blog/building-cross-platform-desktop-applications-wails/)

**Flutter Desktop:**
- [State of Flutter 2026](https://devnewsletter.com/p/state-of-flutter-2026/)
- [Flutter Desktop Support](https://flutter.dev/multi-platform/desktop)
- [Flutter 2025 Features & Enhancements](https://dcm.dev/blog/2025/12/23/top-flutter-features-2025)
- [Flutter Direct Native Interop Initiative](https://medium.com/@001.shabbirhussain/flutters-2026-horizon-unpacking-the-roadmap-and-flutter-4-0-teasers-3a67cfeebd52)

**.NET MAUI:**
- [.NET MAUI Official Documentation](https://dotnet.microsoft.com/en-us/apps/maui)
- [MAUI Avalonia Linux & Browser Support](https://www.theregister.com/2025/11/13/dotnet_maui_linux_avalonia/)
- [MAUI 2025 Development Guide](https://niotechone.com/blog/net-maui-is-changing-cross-platform-development-in-2025/)

**Framework Comparison:**
- [Web to Desktop Framework Comparison (GitHub)](https://github.com/Elanis/web-to-desktop-framework-comparison)
- [Wails vs Tauri Benchmarking](https://muthuishere.medium.com/%EF%B8%8F-micro-benchmarking-desktop-frameworks-wails-go-vs-tauri-rust-599296bed2e2)
- [Desktop Framework Decision Matrix](https://gary-yin.com/posts/the-future-of-desktop-apps/)

---

## 15. Conclusion

**As of February 2026**, the desktop application framework landscape has matured significantly:

- **Tauri 2.0** has emerged as the modern default for new projects, offering unmatched efficiency
- **Electron** remains dominant for teams with JavaScript ecosystem investment
- **Flutter Desktop** is production-ready and ideal for cross-platform strategies
- **Wails** serves the Go developer community effectively
- **.NET MAUI** expanding platform support with Avalonia backend

**The 1/10th Bundle Size Promise**: Tauri delivers on its promise of ~10x smaller bundles than Electron (2.5-10 MB vs 100-300+ MB), with corresponding memory and startup benefits. However, this comes with learning Rust and rebuilding backend logic.

**Choose based on:**
1. **Team expertise** (JavaScript → Electron; Rust-curious → Tauri; Go → Wails; C# → MAUI; cross-platform → Flutter)
2. **Resource constraints** (extreme efficiency → Tauri; reasonable resources → Electron)
3. **Ecosystem needs** (broad libraries → Electron; security paramount → Tauri)
4. **Platform requirements** (Windows/macOS → any; Linux critical → Tauri/Wails; mobile+desktop → Flutter)
5. **Time to market** (existing JavaScript → Electron; greenfield → Tauri for efficiency or Flutter for code reuse)

The "right" choice depends on your specific constraints. For most new projects in 2026, **Tauri 2.0 represents the modern default**, but Electron remains the safe choice for teams prioritizing ecosystem depth over resource efficiency.

---

## Related References
- [Cross-Platform Mobile Development: 2025/2026 Tech Stack Advisor](./14-mobile-cross-platform.md) — Cross-platform patterns and approaches
- [Frontend JavaScript Frameworks 2026: Comprehensive Reference](./01-frontend-frameworks.md) — Frontend framework choice for desktop UI
- [Backend Node.js/Bun/Deno: Runtimes & Frameworks](./04-backend-node.md) — Backend runtime for desktop apps
- [Modern Testing Strategies & Tools (2025-2026)](./53-testing-strategies.md) — Testing frameworks for desktop applications
- [Monorepo Developer Experience & Tooling Reference](./49-monorepo-dx-tooling.md) — Monorepo patterns for desktop/web codebases

---

<!-- PRICING_STABILITY: MODERATE | Updated: 2026-03-03 | Tool/platform pricing changes annually. Verify before critical decisions. -->
