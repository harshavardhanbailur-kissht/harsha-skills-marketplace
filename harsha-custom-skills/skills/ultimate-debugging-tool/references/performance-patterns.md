# Performance Fix Patterns with Context Awareness

Comprehensive template-based fixes organized P1-P7 with context detection and confidence scoring.

---

## Category P1: Animation & Rendering Jank

### P1-001: Animating Layout Properties

**Issue Code**: P1-001
**Issue Name**: Layout Property Animation

**Why It's Slow:**
Layout properties (width, height, top, left, margin, padding) trigger the browser to recalculate positions of all affected elements, then repaint, then composite. This can take 10-100ms.

**Detection Pattern:**
```regex
transition:\s*[^;]*(width|height|top|left|right|bottom|margin|padding)
animation:\s*[^;]*(width|height|top|left|right|bottom|margin|padding)
@keyframes\s+\w+\s*\{[^}]*(width|height|top|left|margin|padding)
```

**Context Check**: Is this intentional? Layout animation is rarely needed. However, some design systems require it (e.g., expanding sidebars, accordion menus). Check skill type and project context. For 3D/animation projects, this is higher priority.

**Tier**: Safe (transform alternative is always available)

**Before:**
```css
.card {
  transition: width 0.3s, height 0.3s, margin 0.3s;
}
.card:hover {
  width: 120%;
  height: 120%;
  margin-top: -10px;
}
```

**After:**
```css
.card {
  transition: transform 0.3s;
}
.card:hover {
  transform: scale(1.2) translateY(-10px);
}
```

**Confidence Score**: 0.90

---

### P1-002: Layout Thrashing

**Issue Code**: P1-002
**Issue Name**: Layout Thrashing (Read/Write Interleaving)

**Why It's Slow:**
Reading a layout property (offsetWidth, getBoundingClientRect) forces the browser to synchronously calculate layout. If you then write to the DOM, the layout is invalidated. The next read forces another layout calculation. In a loop, this can take 100ms+.

**Detection Pattern:**
```javascript
// Look for interleaved reads and writes in same scope
offsetWidth|offsetHeight|getBoundingClientRect|getComputedStyle
.*
(style\.|classList|innerHTML|textContent)
```

**Context Check**: Layout reads are sometimes necessary (e.g., scroll spy, masonry layouts). NOT a flag if the code batches reads and writes separately. Check if pattern uses fastdom, requestAnimationFrame batching, or explicit measurement phase.

**Tier**: Moderate (significant impact only in loops over many elements)

**Before:**
```javascript
elements.forEach(el => {
  const width = el.offsetWidth;  // Forces layout
  el.style.width = width + 10 + 'px';  // Invalidates layout
});
```

**After (Option 1: Manual Batching):**
```javascript
const widths = elements.map(el => el.offsetWidth);
elements.forEach((el, i) => {
  el.style.width = widths[i] + 10 + 'px';
});
```

**After (Option 2: requestAnimationFrame):**
```javascript
requestAnimationFrame(() => {
  const widths = elements.map(el => el.offsetWidth);
  elements.forEach((el, i) => {
    el.style.width = widths[i] + 10 + 'px';
  });
});
```

**Confidence Score**: 0.85

---

### P1-003: Missing will-change Cleanup

**Issue Code**: P1-003
**Issue Name**: Persistent will-change (Layer Bloat)

**Why It's Slow:**
`will-change` creates a new compositor layer, consuming GPU memory. If left on permanently, it causes memory bloat and can actually slow things down on mobile.

**Detection Pattern:**
```css
/* Static will-change at top level */
\.element\s*\{[^}]*will-change:\s*\w+[^}]*\}
/* Without :hover, :focus, or @media queries */
```

**Context Check**: NOT a flag if will-change is inside :hover, :focus, or animation definitions. Also acceptable if explicitly scoped to individual animated elements (not parent containers). Mobile projects flag this as high priority due to memory constraints.

**Tier**: Moderate (aggressive on mobile)

**Before:**
```css
.animated {
  will-change: transform, opacity;
  transition: transform 0.3s, opacity 0.3s;
}
```

**After (CSS-only):**
```css
.animated {
  transition: transform 0.3s, opacity 0.3s;
}
.animated:hover,
.animated:focus {
  will-change: transform, opacity;
}
```

**After (JavaScript):**
```javascript
element.addEventListener('mouseenter', () => {
  element.style.willChange = 'transform, opacity';
});
element.addEventListener('transitionend', () => {
  element.style.willChange = 'auto';
});
```

**Confidence Score**: 0.85

---

### P1-004: setTimeout/setInterval for Animations

**Issue Code**: P1-004
**Issue Name**: Timer-Based Animation (Unsynchronized)

**Why It's Slow:**
`setTimeout`/`setInterval` are not synchronized with the browser's refresh rate. They may fire at random times, causing animations to be choppy or miss frames entirely. This also causes issues when tabs are backgrounded.

**Detection Pattern:**
```javascript
// Animation-related code using setTimeout/setInterval
setInterval\s*\([^,]+,\s*(?:16|20|1000\/60)\s*\)
# Context: within animate/render/update/tick function and touching style
```

**Context Check**: NOT a flag if setTimeout is used for non-visual timers (polling, debounce, delays). ALWAYS flag if modifying transform, opacity, or position properties. Also check: is code using time-based delta or fixed increments?

**Tier**: Safe (RAF always superior for visual animations)

**Before:**
```javascript
let position = 0;
setInterval(() => {
  position += 1;
  element.style.transform = `translateX(${position}px)`;
}, 16);
```

**After:**
```javascript
let position = 0;
let lastTime = 0;

function animate(currentTime) {
  const deltaTime = currentTime - lastTime;
  lastTime = currentTime;
  position += 0.1 * deltaTime;
  element.style.transform = `translateX(${position}px)`;
  requestAnimationFrame(animate);
}

requestAnimationFrame(animate);
```

**Confidence Score**: 0.90

---

### P1-006: Scroll Handler Without RAF Throttling

**Issue Code**: P1-006
**Issue Name**: Unthrottled Scroll Handler

**Why It's Slow:**
Scroll events fire at high frequency (100+ times per second). Without throttling via RAF, you're doing expensive work that won't be displayed (browser can only render 60fps max). This blocks the main thread and causes scroll jank.

**Detection Pattern:**
```javascript
addEventListener\s*\(\s*['"]scroll['"].*\)
# Check: is there RAF throttling, debounce, or throttle call?
# Flag if none found
```

**Context Check**: NOT a flag if handler uses debounce/throttle library or RAF wrapping. Check for ticking pattern or scheduler usage. Some frameworks (React) may already throttle, so verify implementation. Passive listeners alone don't solve this (passive only affects scroll start delay, not expensive work).

**Tier**: Safe (RAF wrapping is always safe)

**Before:**
```javascript
window.addEventListener('scroll', () => {
  updateParallax(window.scrollY);
  updateHeader(window.scrollY);
  checkInfiniteScroll(window.scrollY);
});
```

**After:**
```javascript
let ticking = false;

window.addEventListener('scroll', () => {
  if (!ticking) {
    requestAnimationFrame(() => {
      const scrollY = window.scrollY;
      updateParallax(scrollY);
      updateHeader(scrollY);
      checkInfiniteScroll(scrollY);
      ticking = false;
    });
    ticking = true;
  }
}, { passive: true });
```

**Confidence Score**: 0.90

---

### P1-007: Non-passive Touch/Wheel Listeners

**Issue Code**: P1-007
**Issue Name**: Missing passive Event Listener Flag

**Why It's Slow:**
By default, touch and wheel event listeners can call `preventDefault()`, so the browser must wait for your handler before scrolling. This adds ~100ms delay to every scroll on mobile.

**Detection Pattern:**
```javascript
addEventListener\s*\(\s*['"](?:touchstart|touchmove|wheel)['"]\s*,\s*[^}]+\)
# Without { passive: true } option
```

**Context Check**: ALWAYS flag this. However, if code calls preventDefault() inside handler, the developer may have intentionally omitted passive (though this is rare and usually wrong). Check if preventDefault is actually needed. If code is just tracking touch position (parallax, pinch zoom), passive is always safe.

**Tier**: Safe (adding passive is always safe unless preventDefault is actually needed)

**Before:**
```javascript
element.addEventListener('touchstart', handleTouch);
element.addEventListener('touchmove', handleMove);
element.addEventListener('wheel', handleWheel);
```

**After:**
```javascript
element.addEventListener('touchstart', handleTouch, { passive: true });
element.addEventListener('touchmove', handleMove, { passive: true });
element.addEventListener('wheel', handleWheel, { passive: true });
```

**Note**: Only omit passive if preventDefault() is genuinely needed (custom scroll prevention). This is rare.

**Confidence Score**: 0.95

---

## Category P2: JavaScript Performance

### P2-001: Long Task Blocking Main Thread

**Why It's Slow:**
Any JavaScript task >50ms blocks the main thread, preventing user input response and animation updates. This directly impacts INP (Interaction to Next Paint).

**Detection:**
```javascript
// Monitor with PerformanceObserver
new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    console.warn(`Long task: ${entry.duration}ms`);
  }
}).observe({ entryTypes: ['longtask'] });
```

**Before:**
```javascript
function processLargeArray(items) {
  items.forEach(item => {
    // Heavy processing for each item
    heavyComputation(item);
  });
}
```

**After (Option 1: Chunking with scheduler.yield):**
```javascript
async function processLargeArray(items) {
  const CHUNK_SIZE = 100;

  for (let i = 0; i < items.length; i += CHUNK_SIZE) {
    const chunk = items.slice(i, i + CHUNK_SIZE);

    chunk.forEach(item => heavyComputation(item));

    // Yield to main thread
    if (i + CHUNK_SIZE < items.length) {
      await scheduler.yield?.() || await new Promise(r => setTimeout(r, 0));
    }
  }
}
```

**After (Option 2: Web Worker):**
```javascript
// main.js
const worker = new Worker('processor.js');
worker.postMessage({ items: largeArray });
worker.onmessage = (e) => {
  console.log('Processed:', e.data.result);
};

// processor.js
self.onmessage = (e) => {
  const result = e.data.items.map(item => heavyComputation(item));
  self.postMessage({ result });
};
```

**Confidence:** 75% (requires understanding of specific computation)

---

### P2-004: Missing Debounce/Throttle

**Why It's Slow:**
Rapid-fire events (resize, scroll, input) can trigger expensive operations hundreds of times per second.

**Detection Pattern:**
```javascript
addEventListener\s*\(\s*['"](?:resize|input|keyup|keydown|mousemove)['"]\s*,\s*(?!debounce|throttle)
```

**Before:**
```javascript
input.addEventListener('input', (e) => {
  // Expensive search operation on every keystroke
  performSearch(e.target.value);
});
```

**After (Debounce - wait until user stops):**
```javascript
function debounce(fn, delay) {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), delay);
  };
}

const debouncedSearch = debounce(performSearch, 300);
input.addEventListener('input', (e) => {
  debouncedSearch(e.target.value);
});
```

**After (Throttle - limit frequency):**
```javascript
function throttle(fn, limit) {
  let inThrottle;
  return (...args) => {
    if (!inThrottle) {
      fn(...args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

const throttledScroll = throttle(handleScroll, 100);
window.addEventListener('scroll', throttledScroll);
```

**Confidence:** 85%

---

## Category P3: React-Specific

### P3-001: Inline Object/Array in Render

**Why It's Slow:**
Every render creates a new object/array reference. React's shallow comparison sees it as changed, triggering unnecessary re-renders of child components.

**Detection Pattern:**
```jsx
// Inline objects in JSX
<Component style={{ color: 'red' }} />
<Component options={['a', 'b', 'c']} />
<Component config={{ key: 'value' }} />
```

**Before:**
```jsx
function Parent({ theme }) {
  return (
    <ExpensiveChild
      style={{ background: theme.bg, color: theme.text }}
      options={['option1', 'option2']}
      handlers={{ onClick: () => {}, onHover: () => {} }}
    />
  );
}
```

**After:**
```jsx
// Move static values outside component
const OPTIONS = ['option1', 'option2'];

function Parent({ theme }) {
  // Memoize dynamic values
  const style = useMemo(
    () => ({ background: theme.bg, color: theme.text }),
    [theme.bg, theme.text]
  );

  const handlers = useMemo(
    () => ({ onClick: () => {}, onHover: () => {} }),
    []
  );

  return (
    <ExpensiveChild
      style={style}
      options={OPTIONS}
      handlers={handlers}
    />
  );
}
```

**Confidence:** 85%

---

### P3-002: Missing memo on Expensive Component

**Why It's Slow:**
Without `memo()`, a component re-renders every time its parent re-renders, even if its props haven't changed.

**Detection:**
```jsx
// Component with expensive render not wrapped in memo
// Indicators of expensive: maps over large arrays, complex calculations
function ExpensiveList({ items }) {
  return items.map(item => <ComplexItem key={item.id} {...item} />);
}
```

**Before:**
```jsx
function DataTable({ data, sortConfig }) {
  const sortedData = [...data].sort(/* complex sort */);

  return (
    <table>
      {sortedData.map(row => (
        <TableRow key={row.id} data={row} />
      ))}
    </table>
  );
}
```

**After:**
```jsx
const DataTable = memo(function DataTable({ data, sortConfig }) {
  const sortedData = useMemo(
    () => [...data].sort(/* complex sort */),
    [data, sortConfig]
  );

  return (
    <table>
      {sortedData.map(row => (
        <TableRow key={row.id} data={row} />
      ))}
    </table>
  );
});

const TableRow = memo(function TableRow({ data }) {
  return <tr>{/* render row */}</tr>;
});
```

**Confidence:** 80%

---

### P3-003: Missing useCallback for Handlers

**Why It's Slow:**
Function references change on every render. If passed to memoized children, they'll re-render unnecessarily.

**Before:**
```jsx
function Parent() {
  const [count, setCount] = useState(0);

  // New function reference every render
  const handleClick = () => {
    console.log('clicked');
  };

  return <MemoizedChild onClick={handleClick} />;
}
```

**After:**
```jsx
function Parent() {
  const [count, setCount] = useState(0);

  // Stable function reference
  const handleClick = useCallback(() => {
    console.log('clicked');
  }, []);

  return <MemoizedChild onClick={handleClick} />;
}
```

**Confidence:** 85%

---

## Category P4: Three.js / WebGL

### P4-001: Object Creation in Render Loop

**Why It's Slow:**
Creating objects (especially Three.js Vector3, Matrix4, etc.) in the render loop causes:
1. Memory allocation on heap
2. Garbage collection pressure
3. GC pauses causing frame drops

**Detection Pattern:**
```javascript
// new Vector3/Quaternion/Matrix inside animate/render/update function
function\s+(animate|render|update|tick|loop)\s*\([^)]*\)\s*\{[^}]*new\s+(THREE\.)?(Vector[234]|Quaternion|Matrix[34]|Euler|Color|Box[23]|Sphere)
```

**Before:**
```javascript
function animate() {
  requestAnimationFrame(animate);

  // BAD: New objects every frame = 60 allocations/second
  const direction = new THREE.Vector3(0, 1, 0);
  const target = new THREE.Vector3().copy(camera.position);
  const rotation = new THREE.Quaternion();

  mesh.position.lerp(target, 0.1);
}
```

**After:**
```javascript
// Pre-allocate outside render loop
const _direction = new THREE.Vector3();
const _target = new THREE.Vector3();
const _rotation = new THREE.Quaternion();

function animate() {
  requestAnimationFrame(animate);

  // GOOD: Reuse pre-allocated objects
  _direction.set(0, 1, 0);
  _target.copy(camera.position);

  mesh.position.lerp(_target, 0.1);
}
```

**Confidence:** 95%

---

### P4-002: Direct GSAP Animation (Not Proxy)

**Why It's Slow:**
GSAP doesn't understand Three.js objects. Directly animating `mesh.position` causes GSAP to store incorrect internal state, leading to jumpy animations.

**Detection Pattern:**
```javascript
gsap\.(to|from|fromTo)\s*\(\s*\w+\.(position|rotation|scale|quaternion)
```

**Before:**
```javascript
// BAD: GSAP directly on Three.js object
gsap.to(mesh.position, {
  x: 5,
  y: 2,
  duration: 2,
  ease: 'power2.out'
});
```

**After:**
```javascript
// GOOD: Proxy object pattern
const animationState = {
  x: mesh.position.x,
  y: mesh.position.y,
  z: mesh.position.z
};

gsap.to(animationState, {
  x: 5,
  y: 2,
  duration: 2,
  ease: 'power2.out',
  onUpdate: () => {
    mesh.position.set(animationState.x, animationState.y, animationState.z);
  }
});
```

**Confidence:** 90%

---

### P4-003: Missing Resource Disposal

**Why It's Slow:**
Three.js resources (geometries, materials, textures) persist in GPU memory until explicitly disposed. Without cleanup, memory grows continuously.

**Detection Pattern:**
```javascript
// React: useEffect without disposal cleanup
useEffect\s*\([^)]*\{[^}]*new THREE\.(Geometry|Material|Texture|Mesh)[^}]*(?!\bdispose\b)

// Check for missing dispose calls in component unmount
```

**Before:**
```javascript
useEffect(() => {
  const geometry = new THREE.BoxGeometry(1, 1, 1);
  const material = new THREE.MeshStandardMaterial({ color: 0xff0000 });
  const mesh = new THREE.Mesh(geometry, material);
  scene.add(mesh);

  // No cleanup!
}, []);
```

**After:**
```javascript
useEffect(() => {
  const geometry = new THREE.BoxGeometry(1, 1, 1);
  const material = new THREE.MeshStandardMaterial({ color: 0xff0000 });
  const mesh = new THREE.Mesh(geometry, material);
  scene.add(mesh);

  return () => {
    scene.remove(mesh);
    geometry.dispose();
    material.dispose();
    if (material.map) material.map.dispose();
    if (material.normalMap) material.normalMap.dispose();
    // Dispose all maps...
  };
}, []);

// Or use a ResourceTracker utility
class ResourceTracker {
  constructor() {
    this.resources = new Set();
  }

  track(resource) {
    this.resources.add(resource);
    return resource;
  }

  dispose() {
    for (const resource of this.resources) {
      if (resource.dispose) resource.dispose();
      if (resource.parent) resource.parent.remove(resource);
    }
    this.resources.clear();
  }
}
```

**Confidence:** 85%

---

### P4-004: High Pixel Ratio on Mobile

**Why It's Slow:**
A 3x pixel ratio means 9x the pixels to render. Most users can't perceive the difference between 2x and 3x, but the GPU load is massive.

**Detection Pattern:**
```javascript
// Missing pixel ratio cap
setPixelRatio\s*\(\s*window\.devicePixelRatio\s*\)
```

**Before:**
```javascript
renderer.setPixelRatio(window.devicePixelRatio);
```

**After:**
```javascript
// Cap at 2 for performance (3x provides minimal visual benefit)
const pixelRatio = Math.min(window.devicePixelRatio, 2);
renderer.setPixelRatio(pixelRatio);
```

**Confidence:** 95%

---

### P4-007: Missing Delta Time Capping

**Why It's Slow:**
When a tab is backgrounded and returns, the delta time can be huge (seconds). This causes animations to "jump" to unexpected positions.

**Before:**
```javascript
const clock = new THREE.Clock();

function animate() {
  requestAnimationFrame(animate);
  const delta = clock.getDelta();

  // If tab was backgrounded, delta could be 5+ seconds
  mesh.position.x += delta * 100;
}
```

**After:**
```javascript
const clock = new THREE.Clock();
const MAX_DELTA = 0.1; // 100ms cap

function animate() {
  requestAnimationFrame(animate);
  const delta = Math.min(clock.getDelta(), MAX_DELTA);

  mesh.position.x += delta * 100;
}
```

**Confidence:** 90%

---

## Category P5: Memory Leaks

### P5-001: Uncleared setInterval/setTimeout

**Detection Pattern:**
```javascript
// setInterval without clearInterval in cleanup
useEffect\s*\([^)]*\{[^}]*setInterval[^}]*(?!\bclearInterval\b)
```

**Before:**
```javascript
useEffect(() => {
  setInterval(() => {
    fetchData();
  }, 5000);
  // No cleanup!
}, []);
```

**After:**
```javascript
useEffect(() => {
  const intervalId = setInterval(() => {
    fetchData();
  }, 5000);

  return () => clearInterval(intervalId);
}, []);
```

**Confidence:** 95%

---

### P5-002: Unremoved Event Listeners

**Detection Pattern:**
```javascript
// addEventListener without removeEventListener in cleanup
useEffect\s*\([^)]*\{[^}]*addEventListener[^}]*(?!\bremoveEventListener\b)
```

**Before:**
```javascript
useEffect(() => {
  const handler = () => console.log('resized');
  window.addEventListener('resize', handler);
  // No cleanup!
}, []);
```

**After (Option 1: removeEventListener):**
```javascript
useEffect(() => {
  const handler = () => console.log('resized');
  window.addEventListener('resize', handler);

  return () => window.removeEventListener('resize', handler);
}, []);
```

**After (Option 2: AbortController):**
```javascript
useEffect(() => {
  const controller = new AbortController();

  window.addEventListener('resize', () => console.log('resized'), {
    signal: controller.signal
  });

  return () => controller.abort();
}, []);
```

**Confidence:** 90%

---

## Category P6: Core Web Vitals

### P6-001: Unoptimized LCP Image

**Detection Pattern:**
```html
<!-- LCP candidate without optimization attributes -->
<img src="hero.jpg" class="hero" />
```

**Before:**
```html
<img src="/images/hero.jpg" alt="Hero" class="hero-image" />
```

**After:**
```html
<link rel="preload" as="image" href="/images/hero.webp" fetchpriority="high" />

<picture>
  <source srcset="/images/hero.avif" type="image/avif" />
  <source srcset="/images/hero.webp" type="image/webp" />
  <img
    src="/images/hero.jpg"
    alt="Hero"
    class="hero-image"
    width="1200"
    height="600"
    fetchpriority="high"
    decoding="async"
  />
</picture>
```

**Confidence:** 90%

---

### P6-003: Missing Image Dimensions

**Detection Pattern:**
```html
<!-- img without width AND height -->
<img src="..." alt="..." />
```

**Before:**
```html
<img src="/photo.jpg" alt="Photo" />
```

**After:**
```html
<img
  src="/photo.jpg"
  alt="Photo"
  width="800"
  height="600"
  loading="lazy"
  decoding="async"
/>
```

**CSS:**
```css
img {
  max-width: 100%;
  height: auto;
}
```

**Confidence:** 95%

---

### P6-004: Dynamic Content Without Reserved Space

**Detection Pattern:**
```javascript
// Dynamically inserted content without container sizing
innerHTML|appendChild|insertAdjacentHTML
// Without accompanying CSS for min-height
```

**Before:**
```html
<div id="ad-container"></div>
<div id="dynamic-content"></div>
```

**After:**
```html
<div id="ad-container" class="ad-slot"></div>
<div id="dynamic-content" class="content-slot"></div>

<style>
  .ad-slot {
    min-height: 250px; /* Reserve space for ad */
    contain: layout;
  }
  .content-slot {
    min-height: 200px; /* Reserve space for dynamic content */
    contain: layout;
  }
</style>
```

**Confidence:** 85%
