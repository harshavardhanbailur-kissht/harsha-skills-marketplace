# Context Detection Reference

Detect project type and intentional performance patterns BEFORE analysis to avoid false positives.

## 1. Project Type Detection Algorithm

Analyze signals in order of priority, accumulate scores, highest type wins.

### Signal Detection

```javascript
// package.json dependency analysis
const signals = {
  '3d-experience': [
    'three', '@react-three/fiber', 'gsap', 'lenis',
    '@pmndrs/postprocessing', 'detect-gpu'
  ],
  'animation-site': [
    'gsap', 'framer-motion', 'lenis',
    '@react-three/fiber' // can overlap with 3d
  ],
  'react-spa': ['react', '@vitejs/plugin-react'],
  'data-dashboard': ['recharts', 'chart.js', 'd3', 'plotly.js'],
  'marketing-site': ['next', 'astro'],
  'hybrid': [] // matched last, contains 2+ categories
};

// Import graph analysis: scan .js/.ts/.jsx/.tsx
const importPatterns = {
  'three': /from ['"]three['"]/g,
  'gsap': /from ['"]gsap['"]/g,
  'react-three': /from ['"]@react-three\/fiber['"]/g,
};

// File structure heuristics
const heuristics = {
  'shaders/': 3d-experience,
  'models/': 3d-experience,
  'public/models': 3d-experience,
  'components/': react-spa,
  'pages/': react-spa,
  'app/': react-spa,
  'styles/': 'animation-site|marketing-site',
};

// Config files
const configFiles = {
  'vite.config': universal,
  'next.config': marketing-site,
  'astro.config': marketing-site,
  'tailwind.config': universal,
};
```

### Scoring System

1. Package.json direct deps: +10 points per match
2. Detected imports in codebase: +5 points per file with import
3. File structure presence: +7 points per folder
4. Config file presence: +5 points per file
5. Highest score determines type, ties → 'hybrid'

### Project Types

- **3d-experience**: WebGL, procedural/asset heavy, often premium budgets (30 FPS acceptable)
- **animation-site**: Motion-first, often marketing, 60 FPS expected
- **react-spa**: Standard React apps, 60 FPS expected
- **data-dashboard**: Real-time charts/tables, interactive, 60 FPS baseline
- **marketing-site**: Static + light interactions, 60 FPS expected
- **hybrid**: Multi-category, requires multiple contexts

## 2. Skill Pattern Fingerprinting

### 3D Web Graphics Mastery Patterns

Detect intentional advanced 3D techniques:

```glsl
// Material choice: MeshPhysicalMaterial (not Standard/Basic) = deliberate quality choice
material = new THREE.MeshPhysicalMaterial({
  clearcoat: 1,
  roughness: 0.5,
  metalness: 1,
});

// Post-processing: merged EffectComposer passes (deliberate, premium effect)
const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));
composer.addPass(new BloomPass({ luminanceThreshold: 0.8 }));
composer.addPass(new MotionBlurPass(scene, camera));

// GSAP proxy pattern: animation + sync strategy visible
const proxyObject = { value: 0 };
gsap.to(proxyObject, {
  value: 100,
  duration: 2,
  onUpdate: () => {
    mesh.rotation.z = proxyObject.value * 0.01;
  },
});

// Delta capping: explicit frame rate target
const clock = new THREE.Clock();
function animate() {
  const delta = Math.min(clock.getDelta(), 1/30); // caps to ~33ms
  // ...
}

// GSAP ticker optimization
gsap.ticker.lagSmoothing(0); // disables lag smoothing, full control

// GPU detection + quality tier
import { detectGPU } from 'detect-gpu';
const tier = await detectGPU();
if (tier.tier === 'low') {
  renderer.setPixelRatio(0.5);
  post.effects = post.effects.slice(0, 1); // disable some effects
}

// Studio lighting: 3+ lights = deliberate scene complexity
scene.add(new THREE.DirectionalLight(0xffffff, 1.2));
scene.add(new THREE.DirectionalLight(0x0066ff, 0.8));
scene.add(new THREE.SpotLight(0xff6600, 1.0));

// HDR environment
const pmremGenerator = new THREE.PMREMGenerator(renderer);
const envMap = await new RGBELoader().loadAsync('scene.hdr');
scene.environment = pmremGenerator.fromEquirectangular(envMap).texture;

// GPGPU particles: DataTexture positions = intentional complexity
const positionTexture = new THREE.DataTexture(
  positionData, width, height, THREE.RGBAFormat
);
```

### UI/UX Mastery Patterns

Detect accessibility-first + performance-conscious design:

```css
/* CSS custom properties for design system */
:root {
  --duration-fast: 100ms;
  --duration-normal: 300ms;
  --ease-out: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-in-out: cubic-bezier(0.4, 0, 0.6, 1);
}

/* Respects motion preferences */
@media (prefers-reduced-motion: reduce) {
  * { animation-duration: 0.01ms !important; }
}

/* Skeleton screens: intentional loading pattern */
.skeleton {
  background: linear-gradient(90deg, #f0f0f0 0%, #e0e0e0 50%, #f0f0f0 100%);
  animation: shimmer 2s infinite;
}

/* Touch targets: deliberate accessibility */
button { min-width: 44px; min-height: 44px; }

/* Focus indicators: visible keyboard navigation */
button:focus-visible { outline: 2px solid #0066ff; }
```

## 3. Annotation System

Mark intentional performance patterns in code:

```javascript
// @perf-intentional: Premium 3D effect required for brand experience
const bloomEffect = new UnrealBloomPass();
composer.addPass(bloomEffect);

// @perf-budget: fps=30, gpu=85% — custom budget for this section
// (3D experience can target 30 FPS, higher GPU usage acceptable)
function renderHeavyScene() { /* ... */ }

// @perf-skip — skip performance analysis for this block
// Legacy code, refactoring planned Q2
function oldRenderLoop() { /* ... */ }

// @perf-context: 3d-premium — explicitly declare intentional context
// Overrides auto-detection if needed
function initScene() { /* ... */ }
```

## 4. Decision Tree

When an expensive pattern is detected:

```
Pattern found (high CPU/GPU usage)
├─ Annotated @perf-intentional?
│  └─ YES → SKIP analysis, log as intentional
├─ Matches known skill fingerprint? (3D Graphics, UI/UX Mastery)
│  └─ YES → Flag as "likely intentional", suggest monitor-only mode
├─ Within adaptive budget for detected project type?
│  ├─ 3d-experience: 30 FPS + 80% GPU acceptable
│  ├─ animation-site: 60 FPS + 70% GPU expected
│  ├─ react-spa: 60 FPS + 60% GPU expected
│  ├─ data-dashboard: 60 FPS + 70% GPU expected
│  └─ YES → SKIP, log as within budget
├─ Measured performance actually impacting UX?
│  ├─ Frame drops visible? Jank during scroll/interaction?
│  └─ YES → FLAG as genuine issue, high confidence
└─ None match → FLAG with low confidence, suggest measurement phase
```

**Key Principle**: Never flag intentional patterns as bugs. Measure first, then decide.
