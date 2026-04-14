# Memory and Resource Lifecycle Reference

## 1. Leak Detection Patterns

### WeakRef + FinalizationRegistry
Detect when objects are garbage collected.

```javascript
// Track object lifecycle
const registry = new FinalizationRegistry((key) => {
  console.log(`Object ${key} was garbage collected`);
});

function trackObject(obj, key) {
  registry.register(obj, key);
  return obj;
}

// Example: Track event listener cleanup
let listener = trackObject({
  callback: () => console.log('event'),
  target: document.querySelector('#btn')
}, 'listener-1');

// When listener is dropped, FinalizationRegistry fires
listener = null;
// Output: "Object listener-1 was garbage collected"
```

### Heap Snapshot Diffs
Compare heap snapshots to find growing objects.

```javascript
// Automated heap comparison
async function findLeaks() {
  // Take initial snapshot
  await chrome.devtools.Memory.takeHeapSnapshot();
  
  // Wait and perform actions
  setTimeout(async () => {
    // Take second snapshot
    await chrome.devtools.Memory.takeHeapSnapshot();
    
    // Compare: Look for objects that grew unexpectedly
    // In DevTools: Memory tab > Take snapshot > Compare
  }, 5000);
}

// Script to detect leaking listeners
function getListenerCount() {
  return Object.keys(window.__listeners || {}).length;
}

const initialCount = getListenerCount();
setTimeout(() => {
  const finalCount = getListenerCount();
  if (finalCount > initialCount) {
    console.warn(`Leaked ${finalCount - initialCount} listeners`);
  }
}, 1000);
```

### Detached DOM Detection
Find orphaned DOM nodes still in memory.

```javascript
// Regex pattern to find detached DOM in heap snapshots
// In Chrome DevTools Memory tab > heap snapshot > search for "Detached"

// Script to detect detached nodes programmatically
function findDetachedNodes() {
  const walker = document.createTreeWalker(
    document,
    NodeFilter.SHOW_ELEMENT,
    null,
    false
  );
  
  const attached = new Set();
  let node = walker.nextNode();
  
  while (node) {
    attached.add(node);
    node = walker.nextNode();
  }
  
  // Now check for references that exist but aren't in DOM
  console.log('Live DOM nodes:', attached.size);
}

// Better: Use debug property to mark nodes
function debugDOM(element, id) {
  Object.defineProperty(element, '__debugId', {
    value: id,
    configurable: true
  });
  return element;
}

debugDOM(document.getElementById('main'), 'main-container');
```

---

## 2. Three.js Resource Lifecycle

### Complete Disposal Checklist
Dispose all resources to prevent VRAM leaks.

```javascript
function disposeThreeResource(obj) {
  // 1. Dispose geometry
  if (obj.geometry) {
    obj.geometry.dispose();
  }
  
  // 2. Dispose ALL material properties
  if (obj.material) {
    if (Array.isArray(obj.material)) {
      obj.material.forEach(mat => disposeMaterial(mat));
    } else {
      disposeMaterial(obj.material);
    }
  }
  
  // 3. Remove from parent
  if (obj.parent) {
    obj.parent.remove(obj);
  }
  
  // 4. Dispose children recursively
  obj.children.forEach(child => disposeThreeResource(child));
}

function disposeMaterial(material) {
  // Dispose all textures
  ['map', 'normalMap', 'roughnessMap', 'metalnessMap', 'emissiveMap'].forEach(prop => {
    if (material[prop]) {
      material[prop].dispose();
    }
  });
  
  // Dispose render targets used for post-processing
  if (material.customRenderTarget) {
    material.customRenderTarget.dispose();
  }
  
  // Dispose material itself
  material.dispose();
}
```

### ResourceTracker Pattern
Manage all resources in one place.

```javascript
class ResourceTracker {
  constructor() {
    this.resources = new Map();
  }
  
  track(id, resource) {
    this.resources.set(id, resource);
    return resource;
  }
  
  dispose(id) {
    const resource = this.resources.get(id);
    if (resource) {
      // Dispatch geometry
      if (resource.geometry) resource.geometry.dispose();
      
      // Dispatch material
      if (resource.material) {
        if (Array.isArray(resource.material)) {
          resource.material.forEach(m => m.dispose());
        } else {
          resource.material.dispose();
        }
      }
      
      // Remove from scene
      if (resource.parent) resource.parent.remove(resource);
      
      this.resources.delete(id);
    }
  }
  
  disposeAll() {
    this.resources.forEach((resource) => {
      if (resource.dispose) resource.dispose();
    });
    this.resources.clear();
  }
}

// Usage
const tracker = new ResourceTracker();

const geometry = tracker.track('mesh-1', new THREE.BoxGeometry());
const material = tracker.track('mat-1', new THREE.MeshStandardMaterial());
const mesh = tracker.track('mesh-1', new THREE.Mesh(geometry, material));

scene.add(mesh);

// Later: Clean up
tracker.dispose('mesh-1');
tracker.disposeAll(); // Clean everything
```

---

## 3. React Cleanup Patterns

### useEffect Cleanup
Always return cleanup function to prevent leaks.

```javascript
// BAD: No cleanup
useEffect(() => {
  const handler = () => console.log('scroll');
  window.addEventListener('scroll', handler);
}, []);

// GOOD: Cleanup function
useEffect(() => {
  const handler = () => console.log('scroll');
  window.addEventListener('scroll', handler);
  
  return () => {
    window.removeEventListener('scroll', handler);
  };
}, []);
```

### AbortController for Fetch
Cancel requests when component unmounts.

```javascript
useEffect(() => {
  const controller = new AbortController();
  
  const fetchData = async () => {
    try {
      const response = await fetch('/api/data', {
        signal: controller.signal
      });
      const data = await response.json();
      setData(data);
    } catch (error) {
      if (error.name !== 'AbortError') {
        console.error(error);
      }
    }
  };
  
  fetchData();
  
  // Cleanup: Abort ongoing request
  return () => controller.abort();
}, []);
```

### Subscription Cleanup
Unsubscribe from observables.

```javascript
useEffect(() => {
  // RxJS observable
  const subscription = myObservable$.subscribe(data => {
    setData(data);
  });
  
  // Return cleanup that unsubscribes
  return () => subscription.unsubscribe();
}, []);

// Or for Zustand stores
useEffect(() => {
  const unsubscribe = useStore.subscribe(
    state => state.count,
    (count) => {
      setData(count);
    }
  );
  
  return () => unsubscribe();
}, []);
```

### GSAP Context Cleanup
Revert animations on unmount.

```javascript
useEffect(() => {
  // Create context for easy cleanup
  const ctx = gsap.context(() => {
    gsap.to('.element', { duration: 1, opacity: 0 });
    gsap.fromTo('.other', { x: -100 }, { x: 0 });
  });
  
  // Cleanup: Revert all animations from this context
  return () => ctx.revert();
}, []);
```

---

## 4. Memory Budgets by Device Tier

Device memory varies significantly. Allocate resources accordingly.

```javascript
function getMemoryBudget() {
  const totalJSHeap = performance.memory?.jsHeapSizeLimit || 0;
  
  if (totalJSHeap > 500) {
    return 'ultra'; // 512MB+
  } else if (totalJSHeap > 250) {
    return 'high';  // 256MB+
  } else if (totalJSHeap > 100) {
    return 'mid';   // 128MB+
  } else {
    return 'low';   // 64MB
  }
}

const budgets = {
  ultra: { geometry: 50000, textures: 100, models: 20 },
  high:  { geometry: 25000, textures: 50, models: 10 },
  mid:   { geometry: 10000, textures: 20, models: 5 },
  low:   { geometry: 5000,  textures: 10, models: 2 }
};

const tier = getMemoryBudget();
const budget = budgets[tier];

console.log(`Device tier: ${tier}`, budget);

// Adjust quality based on budget
if (tier === 'low') {
  // Use lower LOD models
  // Reduce texture resolution
  // Decrease particle count
} else if (tier === 'ultra') {
  // Enable high-quality features
}
```

---

## 5. Object Pooling

### Vector3/Matrix4 Pool for Three.js
Reuse objects to reduce garbage collection.

```javascript
class Vector3Pool {
  constructor(capacity = 1000) {
    this.pool = [];
    this.capacity = capacity;
    
    // Pre-allocate vectors
    for (let i = 0; i < capacity; i++) {
      this.pool.push(new THREE.Vector3());
    }
  }
  
  get() {
    if (this.pool.length === 0) {
      console.warn('Vector3Pool exceeded capacity');
      return new THREE.Vector3();
    }
    return this.pool.pop();
  }
  
  release(vector) {
    vector.set(0, 0, 0);
    this.pool.push(vector);
  }
}

// Usage
const vectorPool = new Vector3Pool(100);

function calculateForces(particles) {
  particles.forEach(particle => {
    const force = vectorPool.get();
    
    // Use pooled vector
    force.set(Math.random(), Math.random(), Math.random());
    particle.velocity.add(force);
    
    // Return to pool when done
    vectorPool.release(force);
  });
}
```

### TypedArray Pooling for GPGPU
Reuse buffers for compute shaders.

```javascript
class TypedArrayPool {
  constructor() {
    this.float32Pools = new Map();
  }
  
  getFloat32Array(length) {
    const key = length;
    if (!this.float32Pools.has(key)) {
      this.float32Pools.set(key, []);
    }
    
    const pool = this.float32Pools.get(key);
    if (pool.length > 0) {
      return pool.pop();
    }
    
    return new Float32Array(length);
  }
  
  releaseFloat32Array(array) {
    // Clear the array
    array.fill(0);
    
    // Return to pool
    const pool = this.float32Pools.get(array.length);
    pool.push(array);
  }
}

// Usage in compute shader
const arrayPool = new TypedArrayPool();

function runComputeShader(inputSize) {
  const inputBuffer = arrayPool.getFloat32Array(inputSize);
  const outputBuffer = arrayPool.getFloat32Array(inputSize);
  
  // Fill and process
  fillData(inputBuffer);
  compute(inputBuffer, outputBuffer);
  
  // Release buffers for reuse
  arrayPool.releaseFloat32Array(inputBuffer);
  arrayPool.releaseFloat32Array(outputBuffer);
}
```

### DOM Recycling
Reuse DOM nodes in lists.

```javascript
class DOMPool {
  constructor(creator, capacity = 50) {
    this.creator = creator;
    this.pool = [];
    this.active = new Set();
    
    // Pre-create nodes
    for (let i = 0; i < capacity; i++) {
      this.pool.push(creator());
    }
  }
  
  acquire() {
    let node = this.pool.pop();
    if (!node) {
      node = this.creator();
    }
    this.active.add(node);
    return node;
  }
  
  release(node) {
    if (this.active.has(node)) {
      this.active.delete(node);
      // Reset node state
      node.textContent = '';
      node.className = '';
      this.pool.push(node);
    }
  }
}

// Usage with virtual scrolling
const itemPool = new DOMPool(
  () => {
    const div = document.createElement('div');
    div.className = 'list-item';
    return div;
  },
  50
);

function renderVisibleItems(items, startIndex, endIndex) {
  // Release previously active items
  itemPool.active.forEach(node => itemPool.release(node));
  
  // Acquire and update nodes for visible range
  for (let i = startIndex; i < endIndex; i++) {
    const node = itemPool.acquire();
    node.textContent = items[i].text;
    container.appendChild(node);
  }
}
```

---

## 6. Cache Management

### LRU Cache Implementation
Bounded cache that evicts old entries.

```javascript
class LRUCache {
  constructor(maxSize = 100) {
    this.maxSize = maxSize;
    this.cache = new Map();
  }
  
  get(key) {
    if (!this.cache.has(key)) return null;
    
    // Mark as recently used
    const value = this.cache.get(key);
    this.cache.delete(key);
    this.cache.set(key, value);
    
    return value;
  }
  
  set(key, value) {
    // Delete if exists to update order
    if (this.cache.has(key)) {
      this.cache.delete(key);
    }
    
    // Add to end (most recent)
    this.cache.set(key, value);
    
    // Evict oldest if over capacity
    if (this.cache.size > this.maxSize) {
      const oldestKey = this.cache.keys().next().value;
      this.cache.delete(oldestKey);
    }
  }
  
  clear() {
    this.cache.clear();
  }
}

// Usage: Texture cache
const textureCache = new LRUCache(20);

function getTexture(url) {
  let texture = textureCache.get(url);
  
  if (!texture) {
    texture = new THREE.TextureLoader().load(url);
    textureCache.set(url, texture);
  }
  
  return texture;
}
```

### WeakMap for Lifecycle-Tied Caching
Cache data that lives as long as an object.

```javascript
// BAD: Memory leak - cache never clears
const cache = new Map();
function addToCache(object, data) {
  cache.set(object, data);
}

// GOOD: Clears when object is GC'd
const cache = new WeakMap();
function addToCache(object, data) {
  cache.set(object, data);
  // When object is garbage collected, entry is removed automatically
}

// Example: Cache component state alongside DOM node
const nodeCache = new WeakMap();

function attachData(domNode, data) {
  nodeCache.set(domNode, data);
  
  // Later: data is automatically cleaned when node is removed
}

domNode.addEventListener('beforeunload', () => {
  // nodeCache.get(domNode) automatically becomes undefined
});
```

### Texture Cache Management
Limit VRAM usage.

```javascript
class TextureManager {
  constructor(maxTexturesInVRAM = 50) {
    this.maxTextures = maxTexturesInVRAM;
    this.loadedTextures = new LRUCache(maxTexturesInVRAM);
    this.textureLoader = new THREE.TextureLoader();
  }
  
  async loadTexture(url) {
    // Check cache first
    let texture = this.loadedTextures.get(url);
    if (texture) return texture;
    
    // Load new texture
    texture = await new Promise((resolve, reject) => {
      this.textureLoader.load(url, resolve, undefined, reject);
    });
    
    // Add to cache (old ones evicted automatically)
    this.loadedTextures.set(url, texture);
    
    return texture;
  }
  
  unloadTexture(url) {
    const texture = this.loadedTextures.get(url);
    if (texture) {
      texture.dispose();
      // Remove from cache
      this.loadedTextures.cache.delete(url);
    }
  }
}

const textureManager = new TextureManager(50);
```

---

## 7. Detection Patterns

### Uncleared setInterval/setTimeout

**Detection Regex Pattern:**
```javascript
// Find setInterval without clearInterval
/setInterval\([^)]+\)(?!.*clearInterval)/gm

// Find setTimeout without cleanup
/setTimeout\([^)]+\)(?!.*clearTimeout)/gm
```

**Context Check:**
- Component unmounting without cleanup
- Event listeners setting timeouts repeatedly

**Fix Template:**
```javascript
// BAD: Interval persists after unmount
useEffect(() => {
  setInterval(() => {
    updateData();
  }, 1000);
}, []);

// GOOD: Clear on unmount
useEffect(() => {
  const intervalId = setInterval(() => {
    updateData();
  }, 1000);
  
  return () => clearInterval(intervalId);
}, []);
```

**Verification Approach:**
```javascript
// Monitor active timers
const timers = new Set();
const originalSetInterval = setInterval;
window.setInterval = function(...args) {
  const id = originalSetInterval.apply(this, args);
  timers.add(id);
  return id;
};
const originalClearInterval = clearInterval;
window.clearInterval = function(id) {
  timers.delete(id);
  return originalClearInterval(id);
};

// Report active timers
console.log(`Active timers: ${timers.size}`);
```

---

### Unremoved Event Listeners

**Detection Regex Pattern:**
```javascript
// Find addEventListener without matching removeEventListener
/addEventListener\('([^']+)'[^)]*\)(?!.*removeEventListener.*\1)/gms
```

**Context Check:**
- Multiple addEventListener calls without cleanup
- Event listeners in loops

**Fix Template:**
```javascript
// BAD: Listener not removed
button.addEventListener('click', handler);

// GOOD: Use AbortController
const controller = new AbortController();
button.addEventListener('click', handler, { signal: controller.signal });

// Cleanup: Removes listener
controller.abort();

// Or explicit removal
button.removeEventListener('click', handler);
```

**Verification Approach:**
```javascript
// Check listener count before/after
function getListenerCount(element) {
  // In Chrome DevTools: Use getEventListeners(element) in console
  return getEventListeners(element).length;
}

const before = getListenerCount(button);
addListeners(button);
const after = getListenerCount(button);
console.assert(after === before, `Leaked ${after - before} listeners`);
```

---

### Closure Capturing Large Objects

**Detection Pattern:**
```javascript
// Closure capturing entire object when only property needed
const data = { large: [...Array(1000000)], name: 'x' };
const getName = () => data.name; // Holds entire data in memory
```

**Context Check:**
- Functions defined inside loops
- Callbacks closing over large objects
- Unused variables in closure scope

**Fix Template:**
```javascript
// BAD: Entire object in closure
function setupUI() {
  const config = {
    settings: [...heavyData],
    name: 'app'
  };
  
  button.onclick = () => console.log(config.name);
}

// GOOD: Extract what you need
function setupUI() {
  const config = {
    settings: [...heavyData],
    name: 'app'
  };
  
  const name = config.name;
  config = null; // Help GC
  
  button.onclick = () => console.log(name);
}
```

---

### Three.js Undisposed Resources

**Detection Pattern:**
```javascript
// Regex to find missing .dispose() calls
/new THREE\.(Geometry|Material|Texture|WebGLRenderer|RenderTarget)\([^)]*\)(?!.*\.dispose\(\))/gm
```

**Context Check:**
- Creating geometries in loops
- Materials created but not tracked
- Missing disposal on scene cleanup

**Fix Template:**
```javascript
// BAD: No disposal
function createMesh() {
  return new THREE.Mesh(
    new THREE.BoxGeometry(),
    new THREE.MeshStandardMaterial()
  );
}

// GOOD: Track and dispose
const tracker = new ResourceTracker();

function createMesh() {
  const geometry = tracker.track('geo', new THREE.BoxGeometry());
  const material = tracker.track('mat', new THREE.MeshStandardMaterial());
  return tracker.track('mesh', new THREE.Mesh(geometry, material));
}

// Cleanup
scene.addEventListener('dispose', () => tracker.disposeAll());
```

---

### Unbounded Array/Cache Growth

**Detection Pattern:**
```javascript
// Array growing without bounds
/\w+\.push\([^)]*\).*(?!.*splice.*length|.*pop\()|Array growth in loop/gm
```

**Context Check:**
- Push in loops without corresponding removals
- Cache without size limit
- Event data accumulating

**Fix Template:**
```javascript
// BAD: Unbounded growth
const events = [];
element.addEventListener('mousemove', (e) => {
  events.push(e);
});

// GOOD: Use LRU or fixed size
const eventQueue = new LRUCache(100);

element.addEventListener('mousemove', (e) => {
  eventQueue.set(Date.now(), e);
});
```

**Verification Approach:**
```javascript
// Monitor array growth
function monitorArray(array, name) {
  const originalPush = array.push;
  array.push = function(...args) {
    console.log(`${name} size: ${this.length} -> ${this.length + args.length}`);
    return originalPush.apply(this, args);
  };
}

monitorArray(myArray, 'myArray');
```
