# Core Web Vitals 2025-2026 Reference

## 1. INP (Interaction to Next Paint) - <200ms Good

### Long Animation Frames API for Attribution
Identify which code caused slow interactions.

```javascript
// Enable LoAF monitoring
const observer = new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    console.log('Long Animation Frame detected:', {
      duration: entry.duration,
      renderDuration: entry.renderDuration,
      scripts: entry.scripts.map(s => ({
        url: s.sourceCharacterIndex,
        duration: s.duration
      }))
    });
  }
});

observer.observe({ type: 'long-animation-frame', buffered: true });
```

### scheduler.yield() for Task Splitting
Break up long tasks to allow browser to handle input.

```javascript
// Before: Blocks input for 500ms
function processLargeDataset(data) {
  for (let i = 0; i < data.length; i++) {
    expensiveComputation(data[i]);
  }
}

// After: Yields control periodically
async function processLargeDataset(data) {
  for (let i = 0; i < data.length; i++) {
    if (i % 10 === 0) {
      await scheduler.yield();
    }
    expensiveComputation(data[i]);
  }
}
```

### Framework Patterns
```javascript
// React: Use useTransition for interactions
const [isPending, startTransition] = useTransition();

const handleClick = () => {
  startTransition(() => {
    setExpensiveState(computeValue());
  });
};

// Next.js: Use loading UI pattern
'use client';
import { useTransition } from 'react';

export default function SearchResults() {
  const [isPending, startTransition] = useTransition();
  const [results, setResults] = useState([]);

  const handleSearch = (query) => {
    startTransition(async () => {
      const data = await fetch(`/api/search?q=${query}`);
      setResults(await data.json());
    });
  };

  return (
    <div>
      <input onChange={(e) => handleSearch(e.target.value)} />
      {isPending && <Spinner />}
      <Results items={results} />
    </div>
  );
}
```

### SPA Considerations
For Single Page Applications, navigation events don't reset interaction tracking. Use:

```javascript
// Mark navigation starts
performance.mark('route-change-start');

// Route handler
router.push('/new-page');

// Mark route complete
window.addEventListener('popstate', () => {
  performance.mark('route-change-end');
  performance.measure(
    'route-transition',
    'route-change-start',
    'route-change-end'
  );
});
```

---

## 2. LCP (Largest Contentful Paint) - <2.5s Good

### fetchpriority="high"
Prioritize critical resources for LCP elements.

```html
<!-- Critical images for hero/LCP -->
<img 
  src="/hero.jpg" 
  fetchpriority="high"
  sizes="(max-width: 600px) 100vw, 600px"
/>

<!-- Critical font for hero text -->
<link 
  rel="preload"
  href="/fonts/hero-font.woff2"
  as="font"
  type="font/woff2"
  fetchpriority="high"
/>
```

### Preload Scanner Setup
```html
<head>
  <!-- Font preload (most impactful for text LCP) -->
  <link rel="preload" href="/fonts/main.woff2" as="font" type="font/woff2">
  
  <!-- Critical CSS preload -->
  <link rel="preload" href="/critical.css" as="style">
  
  <!-- Responsive image with srcset -->
  <link rel="preload" 
    href="/hero-desktop.jpg" 
    as="image" 
    media="(min-width: 800px)">
</head>
```

### Responsive Images with AVIF
```html
<picture>
  <!-- Modern AVIF format (best compression) -->
  <source srcset="/image.avif" type="image/avif">
  <!-- Fallback to WebP -->
  <source srcset="/image.webp" type="image/webp">
  <!-- Final fallback -->
  <img 
    src="/image.jpg" 
    alt="Hero"
    fetchpriority="high"
    sizes="(max-width: 768px) 100vw, 768px"
  />
</picture>
```

### Critical CSS Inlining
```javascript
// Build script to inline critical CSS
const critical = require('critical');

critical.generate({
  src: 'index.html',
  dest: 'index-critical.html',
  inline: true,
  minify: true,
  dimensions: [
    { width: 375, height: 667 },  // Mobile
    { width: 1920, height: 1080 } // Desktop
  ]
});
```

### Font Loading Strategy
```css
/* Modern: font-display: swap for LCP */
@font-face {
  font-family: 'MainFont';
  src: url('/main.woff2') format('woff2');
  font-display: swap; /* Avoid invisible text during load */
}

/* For body text: block briefly, then swap */
body {
  font-family: 'MainFont', sans-serif;
}
```

```javascript
// Preload critical fonts early
const link = document.createElement('link');
link.rel = 'preload';
link.as = 'font';
link.href = '/main.woff2';
link.type = 'font/woff2';
link.fetchPriority = 'high';
document.head.appendChild(link);
```

---

## 3. CLS (Cumulative Layout Shift) - <0.1 Good

### bfcache Impact
Avoid layout shifts when restoring from back/forward cache.

```javascript
// Listen for bfcache restore events
window.addEventListener('pageshow', (event) => {
  if (event.persisted) {
    // Page restored from bfcache - re-render to prevent shifts
    forceReRender();
  }
});

window.addEventListener('pagehide', (event) => {
  if (event.persisted) {
    // About to enter bfcache - save scroll position
    sessionStorage.setItem('scrollPos', window.scrollY);
  }
});
```

### View Transitions for Layout Stability
```javascript
// Smooth navigation without layout shifts
if (document.startViewTransition) {
  document.startViewTransition(() => {
    updateDOM(); // Update causes visual change
  });
}
```

```css
/* Define transition styles */
::view-transition-old(root) {
  animation: fadeOut 0.3s ease-out;
}

::view-transition-new(root) {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeOut {
  to { opacity: 0; }
}

@keyframes fadeIn {
  from { opacity: 0; }
}
```

### Dynamic Content Patterns
```html
<!-- Reserve space for dynamic ads/content -->
<div style="width: 300px; height: 600px; background: #f0f0f0;">
  <!-- Ad will load here -->
</div>

<!-- Form validation messages with reserved space -->
<div style="min-height: 24px;">
  <span class="error" id="error-msg"></span>
</div>
```

### Ad Slot Reservation
```javascript
// Don't let ads cause layout shift
const adContainer = document.getElementById('ad-slot');

// Reserve space before ad loads
adContainer.style.minHeight = '600px';
adContainer.style.minWidth = '300px';

// When ad loads, it fills reserved space
fetch('/api/ads')
  .then(r => r.text())
  .then(html => {
    adContainer.innerHTML = html;
  });
```

---

## 4. TTFB (Time to First Byte) - <600ms Good

### 103 Early Hints
Send early hints while server prepares response.

```javascript
// Node.js Express example
app.get('/', (req, res) => {
  // Send 103 Early Hints with Link headers
  res.writeEarlyHints({
    link: [
      '</fonts/main.woff2>; rel=preload; as=font; type=font/woff2',
      '</styles.css>; rel=preload; as=style',
      '</script.js>; rel=preload; as=script'
    ]
  });
  
  // Continue with regular response
  res.send(renderPage());
});
```

### Streaming Responses
```javascript
// Stream HTML while rendering
app.get('/', async (req, res) => {
  res.write('<!DOCTYPE html><html><head>');
  res.write('<title>Page</title>');
  res.write('</head><body>');
  
  // Send header immediately
  res.flush();
  
  // Stream body content
  res.write('<h1>Content</h1>');
  
  // Slow section with fallback
  res.write('<div id="slow">');
  res.flush();
  
  const data = await slowQuery();
  res.write(data);
  res.write('</div>');
  res.end();
});
```

### Server-Timing Headers
```javascript
// Track backend execution time
app.get('/api/data', (req, res) => {
  const startDB = Date.now();
  const data = await queryDatabase();
  const dbTime = Date.now() - startDB;
  
  res.set('Server-Timing', `db;dur=${dbTime};desc="Database Query"`);
  res.json(data);
});
```

```javascript
// Client-side: Read Server-Timing headers
fetch('/api/data')
  .then(r => {
    const timing = r.headers.get('Server-Timing');
    console.log('Server work:', timing);
    return r.json();
  });
```

---

## 5. Emerging Metrics 2025-2026

### Soft Navigation Performance
Track SPA navigation performance accurately.

```javascript
// Detect soft navigation (history.pushState)
const originalPushState = history.pushState;
history.pushState = function(...args) {
  performance.mark('soft-nav-start');
  
  originalPushState.apply(this, args);
  
  // After route handler completes
  requestIdleCallback(() => {
    performance.mark('soft-nav-end');
    performance.measure('soft-nav', 'soft-nav-start', 'soft-nav-end');
  }, { timeout: 2000 });
};
```

### Animation Smoothness
Monitor frame drops during animations.

```javascript
// Track dropped frames
let lastTime = performance.now();
let frameCount = 0;

function measureFrames() {
  const now = performance.now();
  const frameDelta = now - lastTime;
  
  // 60fps target = 16.67ms per frame
  if (frameDelta > 16.67 * 2) { // Frame drop threshold
    console.warn(`Dropped frame: ${frameDelta.toFixed(2)}ms`);
  }
  
  lastTime = now;
  requestAnimationFrame(measureFrames);
}

measureFrames();
```

---

## 6. Framework-Specific Optimizations

### Next.js 15 App Router
```typescript
// app/layout.tsx - Server Component (no hydration cost)
import { Suspense } from 'react';

export const metadata: Metadata = {
  title: 'My App',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html>
      <head>
        <link rel="preload" href="/fonts/main.woff2" as="font" />
      </head>
      <body>
        <Suspense fallback={<Header.Skeleton />}>
          <Header />
        </Suspense>
        <main>{children}</main>
      </body>
    </html>
  );
}
```

### Remix v2 Loaders
```typescript
// routes/posts.$id.tsx
export async function loader({ params }: LoaderFunctionArgs) {
  // Runs on server, data sent to client
  const post = await db.posts.findById(params.id);
  return json(
    { post },
    {
      headers: {
        'Cache-Control': 'public, max-age=3600, s-maxage=86400',
      },
    }
  );
}

export default function Post() {
  const { post } = useLoaderData<typeof loader>();
  return <article>{post.content}</article>;
}
```

### Astro Islands
```astro
---
// astro-islands.astro - Server-rendered by default
import InteractiveWidget from '../components/InteractiveWidget.jsx';

const data = await getStaticData();
---

<h1>{data.title}</h1>

<!-- Island: Only this hydrates (minimal JS) -->
<InteractiveWidget client:load data={data} />
```

---

## Common Mistakes

| Metric | Mistake | Fix |
|--------|---------|-----|
| LCP | Large uncompressed images | Use AVIF, WebP with fallbacks |
| LCP | Font blocks text rendering | Use `font-display: swap` |
| INP | Long task during interaction | Use `scheduler.yield()` |
| CLS | Ads without reserved space | Set `min-height` containers |
| TTFB | No streaming | Use early hints + streaming |
| INP | No transition for expensive updates | Wrap in `useTransition()` |

---

## Measurement Code

```javascript
// Collect all Core Web Vitals
import {getCLS, getFCP, getFID, getLCP, getTTFB} from 'web-vitals';

getCLS(console.log);
getFCP(console.log);
getFID(console.log);
getLCP(console.log);
getTTFB(console.log);

// Or use PerformanceObserver for real-time monitoring
const observer = new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    if (entry.name === 'largest-contentful-paint') {
      console.log('LCP:', entry.renderTime || entry.loadTime);
    }
  }
});

observer.observe({ entryTypes: ['paint', 'largest-contentful-paint'] });
```
