# Performance Budgets & Core Web Vitals

> 2024-2025 performance standards and optimization techniques

## Core Web Vitals (2025)

### Current Thresholds

| Metric | Good | Needs Improvement | Poor |
|--------|------|-------------------|------|
| **LCP** (Largest Contentful Paint) | ≤2.5s | 2.5-4.0s | >4.0s |
| **INP** (Interaction to Next Paint) | ≤200ms | 200-500ms | >500ms |
| **CLS** (Cumulative Layout Shift) | ≤0.1 | 0.1-0.25 | >0.25 |

> **Note:** INP replaced FID as of March 2024. INP measures responsiveness throughout the page lifecycle, not just first input.

### Current Pass Rates (Chrome UX Report)

| Metric | Mobile | Desktop |
|--------|--------|---------|
| LCP | ~50% | ~64% |
| INP | ~65% | ~97% |
| CLS | ~78% | ~80% |
| **All Three** | **~41%** | **~53%** |

---

## Performance Budget

### Recommended Budgets

| Resource | Budget | Notes |
|----------|--------|-------|
| **Total page weight** | ≤500 KB | Compressed |
| **JavaScript** | ≤170 KB | Compressed |
| **CSS** | ≤50 KB | Compressed |
| **Images (viewport)** | ≤200 KB | Initial viewport |
| **Web fonts** | ≤100 KB | Subset if possible |
| **HTML** | ≤50 KB | Compressed |

### Time-Based Budgets

| Metric | Target | Context |
|--------|--------|---------|
| **Time to First Byte** | ≤800ms | Server response |
| **First Contentful Paint** | ≤1.8s | First content visible |
| **Largest Contentful Paint** | ≤2.5s | Main content visible |
| **Time to Interactive** | ≤3.5s | Fully interactive |
| **Total Blocking Time** | ≤200ms | Main thread blocked |

---

## LCP Optimization

### What Counts as LCP?

- `<img>` elements
- `<image>` inside `<svg>`
- `<video>` poster images
- Elements with `background-image`
- Text blocks (paragraphs, headings)

### LCP Optimization Techniques

#### 1. Preload LCP Image

```html
<!-- In <head> -->
<link rel="preload" as="image" href="hero.webp" fetchpriority="high">

<!-- LCP image with high priority -->
<img 
  src="hero.webp" 
  alt="Hero image"
  fetchpriority="high"
  loading="eager"
  decoding="async"
  width="1200"
  height="600">
```

#### 2. Responsive Images

```html
<img 
  src="hero-800.webp"
  srcset="
    hero-400.webp 400w,
    hero-800.webp 800w,
    hero-1200.webp 1200w"
  sizes="100vw"
  alt="Hero image"
  width="1200"
  height="600">
```

#### 3. Modern Image Formats

```html
<picture>
  <source srcset="hero.avif" type="image/avif">
  <source srcset="hero.webp" type="image/webp">
  <img src="hero.jpg" alt="Hero image">
</picture>
```

#### 4. Critical CSS Inline

```html
<head>
  <style>
    /* Critical above-fold CSS - keep under 14KB */
    body { margin: 0; font-family: system-ui; }
    .hero { height: 100vh; display: flex; }
    /* ... */
  </style>
  <link rel="preload" href="styles.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
  <noscript><link rel="stylesheet" href="styles.css"></noscript>
</head>
```

---

## INP Optimization

### Understanding INP

INP measures the time from user interaction to next paint. Unlike FID, it considers all interactions throughout the page lifecycle.

### INP Optimization Techniques

#### 1. Break Long Tasks with scheduler.yield()

```javascript
// Modern approach (Chrome 129+)
async function processLargeList(items) {
  for (const item of items) {
    processItem(item);
    
    // Yield to main thread periodically
    if (shouldYield()) {
      await scheduler.yield();
    }
  }
}

// Fallback for older browsers
function shouldYield() {
  return performance.now() - lastYield > 50; // 50ms max
}

async function yieldToMain() {
  if ('scheduler' in window && 'yield' in scheduler) {
    return scheduler.yield();
  }
  return new Promise(resolve => setTimeout(resolve, 0));
}
```

#### 2. Use requestIdleCallback

```javascript
// Process non-urgent work during idle time
function processNonUrgentWork(items) {
  let i = 0;
  
  function processChunk(deadline) {
    while (i < items.length && deadline.timeRemaining() > 0) {
      processItem(items[i]);
      i++;
    }
    
    if (i < items.length) {
      requestIdleCallback(processChunk);
    }
  }
  
  requestIdleCallback(processChunk);
}
```

#### 3. Optimize Event Handlers

```javascript
// Debounce scroll handlers
let ticking = false;
window.addEventListener('scroll', () => {
  if (!ticking) {
    requestAnimationFrame(() => {
      // Handle scroll
      updateScrollPosition();
      ticking = false;
    });
    ticking = true;
  }
});

// Use passive listeners when not preventing default
element.addEventListener('touchstart', handler, { passive: true });
```

#### 4. Code Splitting

```javascript
// Dynamic imports for non-critical features
async function openModal() {
  const { Modal } = await import('./Modal.js');
  new Modal().show();
}

// Route-based splitting
const routes = {
  '/dashboard': () => import('./pages/Dashboard.js'),
  '/settings': () => import('./pages/Settings.js'),
};
```

---

## CLS Optimization

### Common CLS Causes

1. Images without dimensions
2. Ads/embeds without reserved space
3. Dynamically injected content
4. Web fonts causing FOIT/FOUT
5. Animations that trigger layout

### CLS Optimization Techniques

#### 1. Always Set Image Dimensions

```html
<!-- Always include width and height -->
<img src="photo.jpg" width="800" height="600" alt="">

<!-- CSS aspect ratio as fallback -->
<style>
.image-container {
  aspect-ratio: 4/3;
  width: 100%;
}
</style>
```

#### 2. Reserve Space for Dynamic Content

```css
/* Reserve space for ads */
.ad-slot {
  min-height: 250px;
  background: var(--placeholder);
}

/* Skeleton loading */
.skeleton {
  height: 200px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

#### 3. Font Display Strategy

```css
/* Use font-display: swap */
@font-face {
  font-family: 'CustomFont';
  src: url('font.woff2') format('woff2');
  font-display: swap;
}

/* Or use font-display: optional to avoid FOUT entirely */
@font-face {
  font-family: 'CustomFont';
  src: url('font.woff2') format('woff2');
  font-display: optional;
}
```

#### 4. Avoid Layout-Triggering Animations

```css
/* ❌ Bad: triggers layout */
.animated {
  animation: slideIn 0.3s;
}

@keyframes slideIn {
  from { margin-left: -100px; } /* Triggers layout */
  to { margin-left: 0; }
}

/* ✅ Good: GPU-accelerated */
.animated {
  animation: slideIn 0.3s;
}

@keyframes slideIn {
  from { transform: translateX(-100px); } /* No layout */
  to { transform: translateX(0); }
}
```

---

## Image Optimization

### Format Priority

1. **AVIF** — Best compression (30-50% smaller than WebP)
2. **WebP** — Good support, 25-35% smaller than JPEG
3. **JPEG** — Universal fallback for photos
4. **PNG** — For images requiring transparency
5. **SVG** — For icons, illustrations, logos

### Responsive Image Implementation

```html
<picture>
  <!-- AVIF for modern browsers -->
  <source 
    type="image/avif"
    srcset="
      image-400.avif 400w,
      image-800.avif 800w,
      image-1200.avif 1200w"
    sizes="(max-width: 600px) 100vw, 50vw">
  
  <!-- WebP fallback -->
  <source 
    type="image/webp"
    srcset="
      image-400.webp 400w,
      image-800.webp 800w,
      image-1200.webp 1200w"
    sizes="(max-width: 600px) 100vw, 50vw">
  
  <!-- JPEG fallback -->
  <img 
    src="image-800.jpg"
    srcset="
      image-400.jpg 400w,
      image-800.jpg 800w,
      image-1200.jpg 1200w"
    sizes="(max-width: 600px) 100vw, 50vw"
    alt="Description"
    width="1200"
    height="800"
    loading="lazy"
    decoding="async">
</picture>
```

### Lazy Loading

```html
<!-- Native lazy loading (most images) -->
<img src="photo.jpg" loading="lazy" alt="">

<!-- Never lazy load LCP image -->
<img src="hero.jpg" loading="eager" fetchpriority="high" alt="">

<!-- Lazy load with JavaScript for complex scenarios -->
<img data-src="photo.jpg" class="lazy" alt="">

<script>
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const img = entry.target;
      img.src = img.dataset.src;
      observer.unobserve(img);
    }
  });
}, { rootMargin: '200px' });

document.querySelectorAll('.lazy').forEach(img => observer.observe(img));
</script>
```

---

## JavaScript Optimization

### Bundle Size Budget

| Category | Budget |
|----------|--------|
| Core app | ≤100 KB |
| Route bundles | ≤30 KB each |
| Third-party | ≤50 KB total |
| **Total JS** | **≤170 KB** |

### Optimization Techniques

```javascript
// Tree shaking - import only what you need
import { debounce } from 'lodash-es'; // ✅
// import _ from 'lodash'; // ❌ Imports entire library

// Dynamic imports for features
const analytics = await import('./analytics.js');

// Web Workers for heavy computation
const worker = new Worker('worker.js');
worker.postMessage({ data: heavyData });
worker.onmessage = (e) => console.log(e.data);
```

---

## Performance Monitoring

### Web Vitals JavaScript Library

```javascript
import { onLCP, onINP, onCLS } from 'web-vitals';

// Report to analytics
function sendToAnalytics({ name, value, id }) {
  analytics.track('Web Vitals', {
    metric: name,
    value: Math.round(name === 'CLS' ? value * 1000 : value),
    id
  });
}

onLCP(sendToAnalytics);
onINP(sendToAnalytics);
onCLS(sendToAnalytics);
```

### Performance Observer

```javascript
// Monitor LCP
const lcpObserver = new PerformanceObserver((list) => {
  const entries = list.getEntries();
  const lastEntry = entries[entries.length - 1];
  console.log('LCP:', lastEntry.startTime);
});
lcpObserver.observe({ type: 'largest-contentful-paint', buffered: true });

// Monitor long tasks
const longTaskObserver = new PerformanceObserver((list) => {
  list.getEntries().forEach(entry => {
    console.warn('Long task:', entry.duration, 'ms');
  });
});
longTaskObserver.observe({ type: 'longtask', buffered: true });
```

---

## Testing Tools

| Tool | Purpose |
|------|---------|
| **Lighthouse** | Lab testing, actionable recommendations |
| **PageSpeed Insights** | Field + lab data, CrUX data |
| **Chrome DevTools** | Performance profiling |
| **WebPageTest** | Detailed waterfall, filmstrip |
| **CrUX Dashboard** | Real user data trends |

### Lighthouse CI Example

```yaml
# .github/workflows/lighthouse.yml
name: Lighthouse CI
on: [push]
jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: treosh/lighthouse-ci-action@v10
        with:
          configPath: ./lighthouserc.json
          budgetPath: ./budget.json
```

```json
// budget.json
[
  {
    "path": "/*",
    "timings": [
      { "metric": "largest-contentful-paint", "budget": 2500 },
      { "metric": "total-blocking-time", "budget": 200 }
    ],
    "resourceSizes": [
      { "resourceType": "script", "budget": 170 },
      { "resourceType": "stylesheet", "budget": 50 },
      { "resourceType": "total", "budget": 500 }
    ]
  }
]
```

---

## Key Takeaways

1. **Target all three CWV** — LCP ≤2.5s, INP ≤200ms, CLS ≤0.1
2. **Preload LCP image** — Never lazy load it
3. **Break long tasks** — Use scheduler.yield() for responsiveness
4. **Set image dimensions** — Always width/height to prevent CLS
5. **Use modern formats** — AVIF > WebP > JPEG
6. **Inline critical CSS** — Under 14KB
7. **Monitor continuously** — Set up real user monitoring
