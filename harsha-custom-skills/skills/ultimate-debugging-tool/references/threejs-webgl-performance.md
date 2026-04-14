# Three.js/WebGL Performance Debugging Guide

## Principle: Context-Aware Optimization

Three.js premium visual quality is **INTENTIONAL**. Only optimize what's actually causing measured performance issues. Use profiling (Stats.js, DevTools) before and after changes.

---

## INTENTIONAL PATTERNS (NEVER FLAG)

These patterns are taught by 3D Web Graphics Mastery and are deliberate design choices:

- **MeshPhysicalMaterial**: transmission, clearcoat, sheen → premium aesthetics
- **Post-processing stack**: 10 effects via EffectComposer (auto-merged into minimal passes)
- **Studio lighting**: 3-6 lights (key + fill + rim + ambient) → professional look
- **HDR environment maps**: RGBELoader + PMREMGenerator → realistic reflections
- **GSAP proxy pattern**: Animation without mutating Three.js objects directly
- **Delta time capping**: `Math.min(clock.getDelta(), 1/30)` → stable after tab switch
- **GSAP lagSmoothing(0)**: Disable lag smoothing for predictable animation
- **detect-gpu quality tiers**: Device-aware degradation system
- **2x pixel ratio on desktop**: Intentional for retina displays
- **GPGPU particles**: 65k+ via DataTexture (GPU-accelerated)
- **Raymarching shaders**: 100 steps per pixel (intentional visual quality)
- **Bloom intensity 1.0-2.0**: Cinematic glow effect
- **FogExp2 density 0.02-0.05**: Atmospheric depth

---

## GENUINE PERFORMANCE ISSUES (ALWAYS FLAG)

### 1. Object Creation in Render Loop

**Issue**: Allocates memory every frame.

```javascript
// ❌ WRONG - Creates Vector3 every frame
function animate() {
  const newPos = new THREE.Vector3(x, y, z); // Memory leak
  mesh.position.copy(newPos);
  requestAnimationFrame(animate);
}

// ✅ CORRECT - Reuse single instance
const tempVec = new THREE.Vector3();
function animate() {
  tempVec.set(x, y, z);
  mesh.position.copy(tempVec);
  requestAnimationFrame(animate);
}
```

### 2. Missing Resource Disposal

**Issue**: GPU memory accumulates, frame drops worsen over time.

```javascript
// ❌ WRONG
scene.remove(mesh); // Just removes from scene

// ✅ CORRECT - Free GPU memory
mesh.geometry?.dispose();
mesh.material?.dispose();
if (mesh.material.map) mesh.material.map.dispose();
scene.remove(mesh);
```

### 3. Unbounded Texture Loading

**Issue**: No cleanup when loading new assets.

```javascript
// ✅ CORRECT - Dispose old texture before loading new
if (currentTexture) currentTexture.dispose();
const newTexture = await textureLoader.loadAsync(url);
currentTexture = newTexture;
```

### 4. Missing Delta Time Capping

**Issue**: Tab switch → huge delta time → animation jumps.

```javascript
// ❌ WRONG
const delta = clock.getDelta();
position += velocity * delta;

// ✅ CORRECT - Cap delta time
const delta = Math.min(clock.getDelta(), 1/30);
position += velocity * delta;
```

### 5. Direct GSAP Animation of Three.js Objects

**Issue**: Mutates Three.js properties without triggering updates.

```javascript
// ❌ WRONG
gsap.to(mesh.position, { x: 10, duration: 1 });

// ✅ CORRECT - Use proxy pattern
gsap.to({ x: 0 }, {
  x: 10,
  duration: 1,
  onUpdate(self) {
    mesh.position.x = self.targets()[0].x;
  }
});
```

### 6. Missing Quality Tier System on Mobile

**Issue**: High-poly models, 4k textures on mobile → 5-10 FPS.

```javascript
// ✅ CORRECT - Detect device tier
import { detectGPU } from 'detect-gpu';
const gpu = await detectGPU();
const tier = gpu.tier; // 0=low, 3=high
const qualityPresets = {
  0: { pixelRatio: 1, geometryDetail: 'low', textureSize: 256 },
  1: { pixelRatio: 1, geometryDetail: 'medium', textureSize: 512 },
  2: { pixelRatio: 1.5, geometryDetail: 'high', textureSize: 1024 },
  3: { pixelRatio: 2, geometryDetail: 'ultra', textureSize: 2048 }
};
const quality = qualityPresets[tier];
renderer.setPixelRatio(quality.pixelRatio);
```

### 7. Render Loop During Hidden Tab

**Issue**: Wastes GPU power, overheats mobile devices.

```javascript
// ✅ CORRECT - Use Page Visibility API
document.addEventListener('visibilitychange', () => {
  if (document.hidden) {
    cancelAnimationFrame(animationId);
  } else {
    animate();
  }
});
```

### 8. Excessive Draw Calls Beyond Device Budget

Flag if `renderer.info.render.calls > 500` on mobile or `> 2000` on desktop without justification.

---

## GPU vs CPU Bottleneck Identification

### Diagnostic Metrics

| Metric | How to Read | CPU-Bound Sign | GPU-Bound Sign |
|--------|------------|---|---|
| `renderer.info.render.calls` | High = many objects | >500 on mobile | Irrelevant |
| `renderer.info.render.triangles` | High = complex meshes | Irrelevant | >2M triangles |
| Stats.js MS panel | Consistent near 16-33ms | Near frame budget = CPU | Below budget = GPU |
| Resolution change | Lower resolution → FPS↑ | Irrelevant | GPU-bound |
| Shader complexity | Simple → complex | Irrelevant | FPS drops with complex |

### Profiling Steps

1. Run Stats.js (include `stats.min.js` from mrdoob/stats.js)
2. Log `renderer.info` each frame: `console.log(renderer.info.render)`
3. Toggle features (disable bloom, reduce lights) and watch metrics
4. Use Chrome DevTools GPU Panel: throttle GPU (right-click → Performance)

---

## Draw Call Optimization (Tiered)

### SAFE (No Visual Change)
- **InstancedMesh**: Render 1000 identical trees as `InstancedMesh` instead of 1000 separate meshes
- **Geometry Merging**: Merge static buildings into single geometry (use BufferGeometryUtils.mergeGeometries)
- **Texture Atlasing**: Pack 100 2k textures → 1x 4k atlas (requires UV adjustments)

### MODERATE (Minor Overhead)
- **BatchedMesh**: Mix different geometries with single draw call (slight LOD overhead)
- **LOD System**: Switch to low-poly model at distance using THREE.LOD

### AGGRESSIVE (Visual Loss)
- Remove objects from scene (only if off-screen or occluded)
- Reduce geometry detail (fewer vertices → lower fidelity)

---

## Post-Processing Optimization (Tiered)

### SAFE
- Use `pmndrs/postprocessing` EffectComposer (auto-merges passes into 1-2 shader passes)
- Enable `mipmapBlur` on Bloom effect (better quality + faster)

### MODERATE
- Half-resolution for expensive effects: `SSAO(resolution / 2)`, `SSR(resolution / 2)`
- Reduce SSAO sample count: 16 samples (default 9) → 8 samples
- Reduce Bloom pass count: from 5 to 3 mip levels

### AGGRESSIVE
- Disable effects entirely (Bloom, SSAO, Bloom, SSR)
- Use basic ToneMapping instead of ACESFilmicToneMapping

---

## Shader Optimization

```javascript
// Warm-up: Compile all shaders at init
renderer.render(dummyScene, dummyCamera); // Offscreen frame

// Avoid branching in fragment shaders
// ❌ WRONG: if (normal.z > 0.5) color = bright; else color = dark;
// ✅ CORRECT: color = mix(dark, bright, step(0.5, normal.z));

// Use texture LOD hints
// ❌ texture(map, uv)
// ✅ textureLod(map, uv, 0.0) // Explicit LOD

// MAD optimization (fused multiply-add)
// Let GLSL compiler handle: a * b + c → optimizes to single instruction
```

---

## Asset Management

- **Textures**: Use KTX2 compression (production) or ASTC (mobile)
- **Models**: GLTF/GLB with meshopt or Draco compression (vs 50% size reduction)
- **Progressive Loading**: Load low-poly → swap to high-poly after 2 seconds
- **Texture Sizing by Device Tier**:
  - Ultra (desktop, RTX): 2048px
  - High (desktop, GTX): 1024px
  - Medium (mobile high-end): 512px
  - Low (mobile budget): 256px

---

## React Three Fiber Specifics

```javascript
// ✅ Conditional useFrame
useFrame(({ gl, scene, camera }) => {
  if (needsUpdate) { // Only run when necessary
    updateLogic();
  }
});

// ✅ Invalidate-on-demand
const invalidate = useThree(state => state.invalidate);
onClick={() => invalidate()}; // Render one frame on demand

// ⚠️ Watch expensive Drei components
// <Environment /> compiles IBL: expensive, use memoization
// <Reflector /> renders extra pass: half-resolution or skip on mobile
// Use <Suspense> boundaries around 3D assets
```

---

## Quality Tier Dynamic Adjustment

```javascript
// Degrade if <30fps for >2 seconds
let lowFpsCount = 0;
useFrame(({ clock }) => {
  const fps = 1 / clock.getDelta();
  if (fps < 30) {
    lowFpsCount++;
    if (lowFpsCount > 120) degradeQuality(); // 2 sec at 60fps
  } else {
    lowFpsCount = 0;
  }
});

// Require 5 seconds of good FPS before upgrading
let goodFpsCount = 0;
const upgradeQuality = () => {
  goodFpsCount++;
  if (goodFpsCount > 300) upgradeToNextTier(); // 5 sec at 60fps
};

// Degradation order (in sequence)
// 1. Disable SSAO
// 2. Disable shadows
// 3. Reduce particle count (65k → 20k)
// 4. Lower pixel ratio (2 → 1.5)
// 5. Lower geometry detail
```

---

## Performance Budget by Device

| Device | Pixel Ratio | Max Draw Calls | Max Triangles | Effect Budget |
|--------|---|---|---|---|
| Desktop (High) | 2.0 | 2000 | 10M | All effects |
| Desktop (Mid) | 1.5 | 1000 | 5M | Bloom + SSAO |
| Mobile (High) | 1.0 | 300 | 1M | Bloom only |
| Mobile (Low) | 1.0 | 100 | 500k | None |

---

## Quick Diagnostic Checklist

- [ ] Stats.js FPS stable at 60 (desktop) or 30 (mobile)?
- [ ] `renderer.info.render.calls < 500` (mobile) or `< 2000` (desktop)?
- [ ] Textures disposed after removal? Check DevTools Memory tab.
- [ ] No object allocation in render loop (use profiler to verify)?
- [ ] Quality tier system active on mobile targets?
- [ ] Render loop pauses on hidden tab?
- [ ] Delta time capped at 1/30?
- [ ] Shaders compiled at init (warm-up frame)?

**Never optimize without measurement. Intentional patterns are teaching best practices.**
