# Three.js Bug Patterns

**Versions Covered:** Three.js r171+ through r183.2 (WebGPU production-ready since r171; validated April 2, 2026)

### T-001: Memory Leak from Undisposed Resources

**Symptom:** Memory usage grows continuously; browser slows down over time

**Root Cause:** Geometry, Material, or Texture objects not disposed when removed from scene. WebGL memory not freed

**Detection:**
```typescript
// BUGGY - no disposal
function Scene() {
  const [objects, setObjects] = useState([]);

  function addBox() {
    const geometry = new THREE.BoxGeometry();
    const material = new THREE.MeshBasicMaterial();
    const mesh = new THREE.Mesh(geometry, material);

    scene.add(mesh);
    setObjects([...objects, mesh]); // Never disposed
  }

  function removeBox() {
    const mesh = objects.pop();
    scene.remove(mesh); // Memory leak: geometry/material still in VRAM
  }
}
```

**Safe Fix (ResourceTracker Pattern):**
```typescript
class ResourceTracker {
  resources = [];

  track(resource) {
    this.resources.push(resource);
    return resource;
  }

  dispose() {
    this.resources.forEach(resource => {
      if (resource.dispose) {
        resource.dispose();
      } else if (resource.children) {
        // For objects with children
        resource.traverse(child => {
          if (child.geometry) child.geometry.dispose();
          if (child.material) {
            if (Array.isArray(child.material)) {
              child.material.forEach(m => m.dispose());
            } else {
              child.material.dispose();
            }
          }
        });
      }
    });
    this.resources = [];
  }
}

function Scene() {
  const tracker = useRef(new ResourceTracker());
  const [objects, setObjects] = useState([]);

  function addBox() {
    const geometry = tracker.current.track(new THREE.BoxGeometry());
    const material = tracker.current.track(new THREE.MeshBasicMaterial());
    const mesh = new THREE.Mesh(geometry, material);

    scene.add(mesh);
    setObjects([...objects, mesh]);
  }

  function removeBox() {
    const mesh = objects[objects.length - 1];
    scene.remove(mesh);
    mesh.geometry.dispose();
    mesh.material.dispose();
    setObjects(objects.slice(0, -1));
  }

  useEffect(() => {
    return () => tracker.current.dispose(); // Cleanup on unmount
  }, []);
}
```

**UNSAFE Fix:**
```typescript
// DON'T: Try to dispose in useEffect without proper cleanup
function Scene() {
  useEffect(() => {
    const geometry = new THREE.BoxGeometry();
    const mesh = new THREE.Mesh(geometry, new THREE.MeshBasicMaterial());
    scene.add(mesh);

    // Trying to cleanup in same effect
    return () => mesh.geometry.dispose();
    // But what about material? And what if scene.remove wasn't called?
  }, []);
}
```

**Regression Test:**
```typescript
describe('T-001: Memory Leak', () => {
  it('should dispose geometry and material', () => {
    const geometry = new THREE.BoxGeometry();
    const material = new THREE.MeshBasicMaterial();
    const mesh = new THREE.Mesh(geometry, material);

    const geometrySpy = jest.spyOn(geometry, 'dispose');
    const materialSpy = jest.spyOn(material, 'dispose');

    mesh.geometry.dispose();
    mesh.material.dispose();

    expect(geometrySpy).toHaveBeenCalled();
    expect(materialSpy).toHaveBeenCalled();
  });
});
```

---

### T-002: Object Creation in Render Loop

**Symptom:** Frame rate drops over time; garbage collection pauses every few seconds

**Root Cause:** Creating new objects (Vector3, Quaternion, etc.) inside animate loop. Creates garbage every frame

**Detection:**
```typescript
// BUGGY - new Vector3 every frame
function animate() {
  mesh.position.add(new Vector3(0.01, 0, 0)); // 60 new objects per second
  mesh.rotation.applyQuaternion(new Quaternion()); // More garbage
  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}

// BUGGY - objects created in useFrame
function Cube() {
  useFrame(() => {
    const vec = new THREE.Vector3(1, 0, 0);
    meshRef.current.position.add(vec); // Garbage every frame
  });
}
```

**Safe Fix (Pre-allocate Objects):**
```typescript
// Pre-allocate outside loop
const direction = new THREE.Vector3(0.01, 0, 0);
const rotation = new THREE.Quaternion();

function animate() {
  mesh.position.add(direction);
  mesh.applyQuaternion(rotation);
  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}

// Better: reuse with .set()
const velocity = new THREE.Vector3(0.01, 0, 0);

function animate() {
  mesh.position.addScaledVector(velocity, deltaTime);
  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}

// In React Three Fiber
function Cube() {
  const direction = useRef(new THREE.Vector3(0.01, 0, 0));

  useFrame(() => {
    if (meshRef.current) {
      meshRef.current.position.add(direction.current);
    }
  });

  return <mesh ref={meshRef} />;
}
```

**UNSAFE Fix:**
```typescript
// DON'T: Try to pool objects manually without proper management
const pool = [];

function getVector3() {
  if (pool.length) {
    return pool.pop().set(0, 0, 0);
  }
  return new Vector3();
}

function animate() {
  const vec = getVector3();
  mesh.position.add(vec);
  // Forgot to return vec to pool!
  requestAnimationFrame(animate);
}
```

**Regression Test:**
```typescript
describe('T-002: Object Creation', () => {
  it('should not create new objects in animate loop', () => {
    const originalVectorConstructor = THREE.Vector3;
    let constructorCalls = 0;

    THREE.Vector3 = jest.fn(function() {
      constructorCalls++;
      return originalVectorConstructor.call(this, ...arguments);
    });

    // Run one frame
    animate();

    expect(constructorCalls).toBe(0); // No new objects
    THREE.Vector3 = originalVectorConstructor;
  });
});
```

---

### T-003: Render Loop Running in Background Tab

**Symptom:** Battery drains quickly; CPU usage high even when tab is not visible

**Root Cause:** requestAnimationFrame still fires in background tabs (at reduced rate), wasting GPU/CPU resources

**Detection:**
```typescript
// BUGGY - no visibility check
function animate() {
  renderer.render(scene, camera);
  requestAnimationFrame(animate); // Runs even if tab hidden
}
```

**Safe Fix (Page Visibility API):**
```typescript
function animate() {
  if (!document.hidden) {
    renderer.render(scene, camera);
  }
  requestAnimationFrame(animate);
}

// Or pause completely
let isAnimating = true;

document.addEventListener('visibilitychange', () => {
  isAnimating = !document.hidden;
});

function animate() {
  if (isAnimating) {
    renderer.render(scene, camera);
  }
  requestAnimationFrame(animate);
}

// In React Three Fiber (built-in support)
function Canvas3D() {
  return (
    <Canvas frameloop="demand"> {/* Only render on demand */}
      <Scene />
    </Canvas>
  );
}

// Or use dpr to reduce resolution on lower-end devices
<Canvas dpr={Math.min(window.devicePixelRatio, 1.5)}>
  <Scene />
</Canvas>
```

**UNSAFE Fix:**
```typescript
// DON'T: Try to detect visibility with setTimeout
let isVisible = true;

window.onfocus = () => { isVisible = true; };
window.onblur = () => { isVisible = false; };

function animate() {
  if (isVisible) {
    renderer.render(scene, camera);
  }
  requestAnimationFrame(animate);
  // Focus/blur don't reliably detect visibility
}
```

**Regression Test:**
```typescript
describe('T-003: Background Rendering', () => {
  it('should not render when document is hidden', () => {
    const renderSpy = jest.spyOn(renderer, 'render');

    Object.defineProperty(document, 'hidden', {
      writable: true,
      value: true
    });

    animate();

    expect(renderSpy).not.toHaveBeenCalled();
  });
});
```

---

### T-004: Camera Aspect Ratio Not Updated on Resize

**Symptom:** Scene stretches or squashes when window resizes

**Root Cause:** Camera aspect ratio not updated on resize. Projection matrix not updated

**Detection:**
```typescript
// BUGGY - no resize handler
function Scene() {
  const camera = new THREE.PerspectiveCamera(
    75,
    window.innerWidth / window.innerHeight,
    0.1,
    1000
  );

  // Aspect ratio never updates
}
```

**Safe Fix (ResizeObserver):**
```typescript
function Scene() {
  const containerRef = useRef(null);
  const cameraRef = useRef(null);

  useEffect(() => {
    const container = containerRef.current;
    const camera = new THREE.PerspectiveCamera(
      75,
      container.clientWidth / container.clientHeight,
      0.1,
      1000
    );
    cameraRef.current = camera;

    // Use ResizeObserver for accurate sizing
    const resizeObserver = new ResizeObserver(() => {
      const width = container.clientWidth;
      const height = container.clientHeight;

      camera.aspect = width / height;
      camera.updateProjectionMatrix(); // Must call this!

      renderer.setSize(width, height);
    });

    resizeObserver.observe(container);

    return () => resizeObserver.disconnect();
  }, []);

  return <div ref={containerRef} />;
}

// Also handle window resize for full-screen scenes
function Scene() {
  const rendererRef = useRef(null);
  const cameraRef = useRef(null);

  useEffect(() => {
    function onWindowResize() {
      const width = window.innerWidth;
      const height = window.innerHeight;

      cameraRef.current.aspect = width / height;
      cameraRef.current.updateProjectionMatrix();
      rendererRef.current.setSize(width, height);
    }

    window.addEventListener('resize', onWindowResize);
    return () => window.removeEventListener('resize', onWindowResize);
  }, []);
}
```

**UNSAFE Fix:**
```typescript
// DON'T: Update size without updating camera
function Scene() {
  useEffect(() => {
    window.addEventListener('resize', () => {
      renderer.setSize(window.innerWidth, window.innerHeight);
      // Forgot camera.aspect and updateProjectionMatrix!
    });
  }, []);
}
```

**Regression Test:**
```typescript
describe('T-004: Camera Aspect', () => {
  it('should update camera aspect on resize', () => {
    const camera = new THREE.PerspectiveCamera(75, 16 / 9);
    const updateSpy = jest.spyOn(camera, 'updateProjectionMatrix');

    // Simulate resize
    const resizeObserver = new ResizeObserver(() => {
      camera.aspect = 4 / 3;
      camera.updateProjectionMatrix();
    });

    resizeObserver.observe(container);
    // Trigger resize...

    expect(updateSpy).toHaveBeenCalled();
    expect(camera.aspect).toBe(4 / 3);
  });
});
```

---

### T-005: WebGL Context Loss

**Symptom:** Canvas goes black; "WebGL context lost" in console; scene doesn't recover

**Root Cause:** Too many WebGL contexts, GPU driver crash, or browser context limit exceeded

**Detection:**
```typescript
// BUGGY - no context loss handler
function Scene() {
  const renderer = new THREE.WebGLRenderer({ canvas });

  // If context is lost, scene is permanently black
}
```

**Safe Fix:**

**Option 1: WebGPU (Three.js r171+, production-ready since r171):**
```typescript
import { WebGPURenderer } from 'three/webgpu';
import { blendBurn, blendDodge } from 'three/tsl'; // TSL blending renamed

function Scene() {
  const rendererRef = useRef(null);
  const canvasRef = useRef(null);

  useEffect(() => {
    let animationId;

    async function initRenderer() {
      const canvas = canvasRef.current;
      const renderer = new WebGPURenderer({ canvas, antialias: true });

      // WebGPURenderer requires async initialization
      await renderer.init();

      renderer.setSize(window.innerWidth, window.innerHeight);
      renderer.setPixelRatio(window.devicePixelRatio);
      rendererRef.current = renderer;

      // Scene setup
      const scene = new THREE.Scene();
      const camera = new THREE.PerspectiveCamera(
        75,
        window.innerWidth / window.innerHeight,
        0.1,
        1000
      );
      camera.position.z = 5;

      // WebGPURenderer automatically falls back to WebGL2 if WebGPU unavailable
      const geometry = new THREE.BoxGeometry();

      // Use renamed TSL blending functions in WebGPU
      const material = new THREE.MeshBasicMaterial({
        color: 0x00ff00,
        // blendBurn, blendDodge, etc. for WebGPU blending
      });

      const mesh = new THREE.Mesh(geometry, material);
      scene.add(mesh);

      function animate() {
        animationId = requestAnimationFrame(animate);
        mesh.rotation.x += 0.01;
        renderer.render(scene, camera);
      }
      animate();

      return () => {
        cancelAnimationFrame(animationId);
        renderer.dispose();
      };
    }

    initRenderer();
  }, []);

  return <canvas ref={canvasRef} />;
}

// Use CubeRenderTarget instead of WebGLCubeRenderTarget for WebGPU
function CubeMapScene() {
  const rendererRef = useRef(null);

  useEffect(() => {
    async function setup() {
      const renderer = new WebGPURenderer();
      await renderer.init();

      // WebGPU compatible cube render target
      const cubeRenderTarget = new THREE.WebGLCubeRenderTarget(256);
      rendererRef.current = renderer;
    }

    setup();
  }, []);
}
```

**Option 2: WebGL with context loss handler (fallback/legacy):**
```typescript
function Scene() {
  const rendererRef = useRef(null);

  useEffect(() => {
    const canvas = document.querySelector('canvas');
    const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
    rendererRef.current = renderer;

    // Handle context loss for WebGL
    canvas.addEventListener('webglcontextlost', (e) => {
      e.preventDefault();
      console.warn('WebGL context lost, attempting recovery...');
    });

    canvas.addEventListener('webglcontextrestored', () => {
      console.log('WebGL context restored');
      // Renderer automatically recovers on next render
    });

    return () => {
      canvas.removeEventListener('webglcontextlost', null);
      canvas.removeEventListener('webglcontextrestored', null);
      renderer.dispose();
    };
  }, []);

  return <canvas />;
}

// Limit number of contexts (max 8 in most browsers)
function MultiScene() {
  // Share renderer across multiple scenes when possible
  const sharedRenderer = useRef(null);

  useEffect(() => {
    if (!sharedRenderer.current) {
      sharedRenderer.current = new THREE.WebGLRenderer();
    }

    return () => {
      // Don't dispose shared renderer until all scenes done
    };
  }, []);
}
```

**UNSAFE Fix:**
```typescript
// DON'T: Create multiple renderers without managing contexts
function Dashboard() {
  return (
    <>
      <SceneA /> {/* Creates renderer 1 */}
      <SceneB /> {/* Creates renderer 2 */}
      <SceneC /> {/* Creates renderer 3 */}
      <SceneD /> {/* ... could exceed limit */}
    </>
  );
}
```

**Regression Test:**
```typescript
describe('T-005: WebGL Context', () => {
  it('should handle context loss gracefully', () => {
    const canvas = document.querySelector('canvas');
    const lostSpy = jest.fn();
    const restoredSpy = jest.fn();

    canvas.addEventListener('webglcontextlost', lostSpy);
    canvas.addEventListener('webglcontextrestored', restoredSpy);

    // Simulate context loss
    const event = new Event('webglcontextlost');
    canvas.dispatchEvent(event);

    expect(lostSpy).toHaveBeenCalled();
  });
});
```

---
