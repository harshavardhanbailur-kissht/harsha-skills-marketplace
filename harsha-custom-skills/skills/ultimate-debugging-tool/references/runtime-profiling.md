# Runtime Profiling Guide

**Core Principle: MEASURE before optimizing.**

## 1. Performance Observer API

Track real-world performance metrics with native browser APIs.

### Long Animation Frames (LoAF) - Chrome 123+
Replaces deprecated Long Tasks API.

```javascript
const loafObserver = new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    console.log('LoAF Duration:', entry.duration);
    console.log('Scripts:', entry.scripts.map(s => ({
      name: s.name,
      duration: s.duration,
      executionStart: s.executionStart,
      sourceCharPosition: s.sourceCharPosition
    })));
    console.log('Render:', {
      renderStart: entry.renderStart,
      renderEnd: entry.renderEnd
    });
  }
});
loafObserver.observe({ entryTypes: ['long-animation-frame'] });
```

### Event Timing (INP Measurement)
```javascript
const eventObserver = new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    const delay = entry.processingStart - entry.startTime;
    const processing = entry.processingEnd - entry.processingStart;
    const presentation = entry.startTime + entry.duration - entry.processingEnd;
    console.log(`Event: ${entry.name}`, {
      delay, processing, presentation, duration: entry.duration,
      interactionId: entry.interactionId
    });
  }
});
eventObserver.observe({ entryTypes: ['event'] });
```

### Largest Contentful Paint (LCP)
```javascript
const lcpObserver = new PerformanceObserver((list) => {
  const entries = list.getEntries();
  const lastEntry = entries[entries.length - 1];
  console.log('LCP:', lastEntry.renderTime || lastEntry.loadTime, 'ms');
});
lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
```

### Cumulative Layout Shift (CLS)
```javascript
const clsObserver = new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    if (!entry.hadRecentInput) { // Exclude user-input shifts
      console.log('Layout Shift:', entry.value);
    }
  }
});
clsObserver.observe({ entryTypes: ['layout-shift'] });
```

### Resource Timing
```javascript
const resourceObserver = new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    const ttfb = entry.responseStart - entry.fetchStart;
    const download = entry.responseEnd - entry.responseStart;
    console.log(entry.name, { ttfb, download, duration: entry.duration });
  }
});
resourceObserver.observe({ entryTypes: ['resource'] });
```

### Element Timing
```javascript
const elementObserver = new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    console.log('Element render:', entry.element, entry.renderTime);
  }
});
elementObserver.observe({ entryTypes: ['element'] });
```

## 2. DevTools Console Profiling Snippets

### Snippet 1: Frame Time Profiler (5 seconds)
Paste directly into DevTools Console:

```javascript
(async () => {
  const frames = [];
  let rafId;
  const start = performance.now();

  const measureFrame = (now) => {
    if (now - start < 5000) {
      frames.push(now);
      rafId = requestAnimationFrame(measureFrame);
    } else {
      const deltas = [];
      for (let i = 1; i < frames.length; i++) {
        deltas.push(frames[i] - frames[i-1]);
      }
      deltas.sort((a, b) => a - b);

      const avg = deltas.reduce((a, b) => a + b) / deltas.length;
      const p50 = deltas[Math.floor(deltas.length * 0.5)];
      const p95 = deltas[Math.floor(deltas.length * 0.95)];
      const p99 = deltas[Math.floor(deltas.length * 0.99)];
      const jank = deltas.filter(d => d > 16.67).length;
      const severe = deltas.filter(d => d > 50).length;

      console.table({
        'Frame Count': deltas.length,
        'Avg Frame (ms)': avg.toFixed(2),
        'P50 (ms)': p50.toFixed(2),
        'P95 (ms)': p95.toFixed(2),
        'P99 (ms)': p99.toFixed(2),
        'Jank Count (>16.67ms)': jank,
        'Severe Jank (>50ms)': severe
      });
    }
  };

  measureFrame(performance.now());
})();
```

### Snippet 2: Animation Smoothness Scorer
```javascript
(async () => {
  const frames = [];
  const start = performance.now();

  const measure = (now) => {
    if (now - start < 5000) {
      frames.push(now);
      requestAnimationFrame(measure);
    } else {
      const deltas = [];
      for (let i = 1; i < frames.length; i++) {
        deltas.push(frames[i] - frames[i-1]);
      }

      const avg = deltas.reduce((a, b) => a + b) / deltas.length;
      const variance = deltas.reduce((sum, d) => sum + (d - avg) ** 2, 0) / deltas.length;
      const jankCount = deltas.filter(d => d > 16.67).length;
      const jankPercent = (jankCount / deltas.length) * 100;

      const smoothness = Math.max(0, 100 - (Math.sqrt(variance) * 2) - (jankPercent * 0.5));

      console.log('🎬 Smoothness Score:', smoothness.toFixed(0) + '/100');
      console.log('Avg Frame:', avg.toFixed(2) + 'ms');
      console.log('Jank %:', jankPercent.toFixed(1));
      console.log('Worst Frame:', Math.max(...deltas).toFixed(2) + 'ms');
    }
  };

  requestAnimationFrame(measure);
})();
```

### Snippet 3: Memory Growth Monitor
```javascript
(async () => {
  const samples = [];
  const start = performance.now();

  const interval = setInterval(async () => {
    if (performance.memory) {
      samples.push(performance.memory.usedJSHeapSize);
      if (performance.now() - start > 30000) {
        clearInterval(interval);

        const initial = samples[0];
        const final = samples[samples.length - 1];
        const growth = ((final - initial) / initial) * 100;
        const suspectLeak = growth > 10;

        console.table({
          'Initial Heap (MB)': (initial / 1e6).toFixed(2),
          'Final Heap (MB)': (final / 1e6).toFixed(2),
          'Growth (%)': growth.toFixed(2),
          'Leak Suspected': suspectLeak ? '⚠️ Yes' : 'No'
        });
      }
    }
  }, 1000);
})();
```

### Snippet 4: Performance Overlay
Self-contained, paste-and-go live metrics:

```javascript
(async () => {
  const overlay = document.createElement('div');
  overlay.style.cssText = `
    position: fixed; top: 10px; right: 10px; z-index: 9999;
    background: rgba(0,0,0,0.8); color: #0f0; font-family: monospace;
    padding: 10px; border-radius: 4px; font-size: 12px; line-height: 1.5;
  `;
  document.body.appendChild(overlay);

  let lastTime = performance.now();
  let frameCount = 0;

  const updateMetrics = () => {
    frameCount++;
    const now = performance.now();

    if (now - lastTime >= 1000) {
      const fps = frameCount;
      const avgFrameTime = 1000 / fps;
      const heap = performance.memory
        ? (performance.memory.usedJSHeapSize / 1e6).toFixed(1) + 'MB'
        : 'N/A';

      overlay.innerHTML = `FPS: ${fps}<br>Frame: ${avgFrameTime.toFixed(2)}ms<br>Memory: ${heap}`;
      frameCount = 0;
      lastTime = now;
    }

    requestAnimationFrame(updateMetrics);
  };

  requestAnimationFrame(updateMetrics);
})();
```

## 3. Lighthouse Integration

### Node API Setup
```javascript
import lighthouse from 'lighthouse';
import chromeLauncher from 'chrome-launcher';

const runLighthouse = async (url) => {
  const chrome = await chromeLauncher.launch({ chromeFlags: ['--headless'] });
  const options = { logLevel: 'info', output: 'json', port: chrome.port };
  const runnerResult = await lighthouse(url, options);
  await chrome.kill();
  return runnerResult.lhr;
};
```

### Lighthouse CI Config (lighthouserc.json)
```json
{
  "ci": {
    "collect": {
      "url": ["https://example.com"],
      "numberOfRuns": 3
    },
    "assert": {
      "preset": "lighthouse:recommended",
      "assertions": {
        "categories:performance": ["error", { "minScore": 0.9 }],
        "categories:performance": ["warn", { "minScore": 0.8 }]
      }
    }
  }
}
```

### Lighthouse User Flows (Animation Profiling)
```javascript
import { startFlow } from 'lighthouse/lighthouse-core/fraggle-rock/api.js';

const flow = await startFlow(page);
await flow.startTimespan({ stepName: 'Animation Sequence' });
// Trigger animation...
await flow.endTimespan();
const report = await flow.generateReport();
```

## 4. Scheduler API (2025 Stable)

Break long tasks and prioritize work:

```javascript
// Break long task with scheduler.yield()
async function processLargeDataset(items) {
  for (let i = 0; i < items.length; i += 1000) {
    processChunk(items.slice(i, i + 1000));
    await scheduler.yield();
  }
}

// Priority-based execution
scheduler.postTask(() => criticalWork(), { priority: 'user-blocking' });
scheduler.postTask(() => normalWork(), { priority: 'user-visible' });
scheduler.postTask(() => backgroundAnalytics(), { priority: 'background' });
```

## 5. Three.js-Specific Profiling

### Renderer Info Tracking
```javascript
const checkGPUBottleneck = () => {
  const info = renderer.info;
  console.log('Draw Calls:', info.render.calls);
  console.log('Triangles:', info.render.triangles);
  console.log('Programs:', info.programs.length);
  console.log('Memory:', {
    geometries: info.memory.geometries,
    textures: info.memory.textures
  });
};

// GPU bottleneck test: lower resolution → check FPS improvement
renderer.setSize(window.innerWidth / 2, window.innerHeight / 2);
// If FPS increases significantly → GPU-bound
```

### Stats.js Integration
```javascript
const stats = new Stats();
document.body.appendChild(stats.dom);

function animate() {
  stats.begin();
  renderer.render(scene, camera);
  stats.end();
  requestAnimationFrame(animate);
}
```

---

**Remember: Profile real users, measure before guessing, iterate on data.**
