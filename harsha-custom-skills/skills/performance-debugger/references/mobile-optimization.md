# Mobile and Cross-Device Adaptive Performance

## Device Capability Detection

Detect device capabilities at runtime to enable intelligent quality adjustments:

- **GPU Detection**: Use `detect-gpu` library to identify renderer capabilities
- **Memory**: Check `navigator.deviceMemory` (in GB, e.g., 4, 6, 8)
- **CPU Cores**: Detect `navigator.hardwareConcurrency` for threading decisions
- **Network**: Inspect `navigator.connection.effectiveType` (4g, 3g, 2g, slow-4g)
- **GPU Renderer String**: Parse to identify mobile vs desktop GPU (Adreno, Mali, Apple A-series)

## Adaptive Quality System

Implement a tiered quality system that responds to runtime conditions:

1. **Tier Detection**: Classify devices at startup
   - Tier A (High): Flagship devices, desktop, 8GB+ memory, dedicated GPU
   - Tier B (Mid): Mid-range phones, 4-6GB memory, integrated GPU, desktop integrated
   - Tier C (Low): Budget phones, 2-3GB memory, basic GPU, older devices

2. **Preset Mapping**: Map tiers to quality presets
   - Shader quality, texture resolution, draw calls, post-processing effects
   - Update on demand based on FPS monitoring

3. **Runtime FPS Monitoring**: Track frame rate in production
   - Use `performance.now()` or `PerformanceObserver` with `long-animation-frame` entries
   - Sample FPS every 3-5 seconds to avoid overhead

4. **Dynamic Adjustment**: Reduce quality when FPS drops below threshold
   - Threshold: 50 FPS for mobile (target 60), 30 FPS for low-end
   - Drop: shader complexity → texture resolution → draw call count

5. **Hysteresis**: Prevent oscillation between quality levels
   - Upgrade only after sustained 60+ FPS for 5+ seconds
   - Downgrade immediately on FPS drop below 45 FPS

6. **User Override**: Allow manual quality selection
   - Store preference in localStorage with timestamp
   - Respect for session or until device changes

---

## Mobile-Specific Patterns

### Touch Events
- Use **passive event listeners**: `addEventListener('touchmove', fn, { passive: true })`
- Set **touch-action CSS**: `touch-action: pan-y` or `pan-x` for scrollable areas
- Eliminate **300ms tap delay** with viewport meta tag and pointer-events

### iOS Safari Quirks
- **WKWebView GPU limits**: Cap texture size at 2K, reduce draw calls, monitor memory
- **position:fixed issues**: Use transform-based positioning instead; be aware of scroll jank
- **Safe areas**: Respect `env(safe-area-inset-*)` CSS variables for notch/home indicator

### Android Chrome
- **Renderer process limits**: Monitor memory; reduce WebGL context usage
- **Battery awareness**: Disable animations during battery saver mode
- **Chrome DevTools throttling**: Simulate Pixel 4 or similar mid-range device

---

## Network-Aware Loading

Adapt asset quality and loading strategy to network conditions:

- **effectiveType Detection**: Use `navigator.connection.effectiveType`
  - `4g`: Full quality, preload aggressively
  - `3g`: Reduced quality, progressive loading
  - `2g` / `slow-4g`: Minimal quality, essential assets only

- **Adaptive Image Quality**: Serve images at different resolutions
  - Desktop 2K: 2560px width max
  - Mobile 1x: 800px width
  - Mobile 2x: 1200px width
  - Slow network: 600px width max

- **Progressive 3D Loading**: Lazy-load 3D models and textures
  - Load LOD (level of detail) models first
  - Stream high-quality assets in background
  - Replace models on load completion

## Power-Aware Optimization

Reduce battery drain on mobile devices:

- **Battery Detection**: Check `navigator.getBattery()` (deprecated, use `powerPreference` in WebGL)
- **Reduced Animation**: Disable or reduce animation speed when battery < 20% or "Battery Saver" mode
- **Page Visibility API**: Stop rendering, animations, and polling when tab is hidden
  - Use `document.hidden` or `visibilitychange` event
  - Resume when tab regains focus

---

## Responsive 3D Rendering

Adjust 3D rendering quality based on device capability:

- **Pixel Ratio Capping**
  - Mobile: Cap at 1.5x (avoid `window.devicePixelRatio` over 2)
  - Desktop: Allow up to 2x for high-DPI displays
  - Fallback to 1x on very low-memory devices

- **Shadow Quality by Tier**
  - Tier A: 2K shadow maps, PCF filtering
  - Tier B: 1K shadow maps, basic filtering
  - Tier C: Baked shadows or disabled shadows

- **Post-Processing Selection**
  - Tier A: Full pipeline (bloom, depth of field, ambient occlusion)
  - Tier B: Selective effects (bloom only)
  - Tier C: Disabled post-processing

- **Texture Resolution by Device Memory**
  - 8GB+: 2K textures
  - 4-6GB: 1K textures
  - 2GB: 512px textures

---

## Detection Patterns

Flag these patterns when analyzing mobile performance:

1. **Missing passive event listeners** on scroll, touch, or wheel events
   - ALWAYS flag as critical for mobile UX

2. **Missing touch-action CSS** on scrollable containers
   - Flag for any element with scroll handlers

3. **No quality tier system** for 3D sites targeting mobile
   - Moderate priority; essential for 3D performance

4. **Fixed pixel ratio** without capping on mobile
   - Flag if `window.devicePixelRatio` is used directly in calculations without mobile check

5. **Missing Page Visibility API** check
   - Flag for sites with continuous animation or polling

6. **No network-aware image loading**
   - Flag for image-heavy sites without adaptive quality

7. **Unmonitored battery drain**
   - Flag if animations run continuously without battery awareness

---

