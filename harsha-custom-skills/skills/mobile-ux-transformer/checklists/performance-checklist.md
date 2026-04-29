# Performance Checklist

> Core Web Vitals and mobile performance optimization

## Core Web Vitals (2025 Thresholds)

### LCP (Largest Contentful Paint)
**Target: ≤2.5 seconds**

- [ ] LCP element identified and optimized
- [ ] Images above fold use `loading="eager"`
- [ ] LCP image has `fetchpriority="high"`
- [ ] Critical CSS inlined (<14KB)
- [ ] Web fonts preloaded
- [ ] Server response time <600ms (TTFB)
- [ ] No render-blocking resources
- [ ] CDN configured for static assets

### INP (Interaction to Next Paint)
**Target: ≤200 milliseconds**

- [ ] No long tasks >50ms blocking main thread
- [ ] Event handlers debounced/throttled
- [ ] Heavy computation moved to Web Workers
- [ ] `scheduler.yield()` used for long tasks
- [ ] Third-party scripts loaded async/defer
- [ ] Input handlers optimized
- [ ] requestIdleCallback for non-critical work
- [ ] Code splitting implemented

### CLS (Cumulative Layout Shift)
**Target: ≤0.1**

- [ ] All images have width/height attributes
- [ ] Aspect ratio boxes for media
- [ ] Font fallbacks match web font metrics
- [ ] `font-display: swap` or `optional`
- [ ] Reserved space for dynamic content
- [ ] Ads/embeds have reserved dimensions
- [ ] No content injected above viewport
- [ ] Animations use `transform`/`opacity` only

---

## Resource Budgets

### Total Page Weight
| Resource | Budget | Actual |
|----------|--------|--------|
| **Total** | ≤500KB | |
| HTML | ≤50KB | |
| CSS | ≤50KB | |
| JavaScript | ≤170KB | |
| Images | ≤200KB | |
| Fonts | ≤50KB | |

### Request Count
| Type | Budget | Actual |
|------|--------|--------|
| **Total requests** | ≤50 | |
| JS files | ≤10 | |
| CSS files | ≤3 | |
| Font files | ≤4 | |

---

## Image Optimization

- [ ] Modern formats (AVIF → WebP → JPEG)
- [ ] Responsive images with `srcset`
- [ ] Appropriate `sizes` attribute
- [ ] Lazy loading for below-fold images
- [ ] Image CDN with auto-optimization
- [ ] Correct dimensions (no oversized images)
- [ ] Placeholder/blur-up for lazy images

```html
<!-- Optimized image example -->
<img 
  src="image-800.webp"
  srcset="image-400.webp 400w, image-800.webp 800w, image-1200.webp 1200w"
  sizes="(max-width: 600px) 100vw, 50vw"
  width="800"
  height="600"
  loading="lazy"
  decoding="async"
  alt="Description">
```

---

## JavaScript Optimization

- [ ] Code splitting by route
- [ ] Tree shaking enabled
- [ ] Unused code removed
- [ ] Third-party scripts audited
- [ ] Scripts loaded async/defer
- [ ] Module/nomodule pattern for modern browsers
- [ ] Service worker for caching

```html
<!-- Modern loading pattern -->
<script type="module" src="app.modern.js"></script>
<script nomodule src="app.legacy.js"></script>
```

---

## CSS Optimization

- [ ] Critical CSS inlined
- [ ] Non-critical CSS loaded async
- [ ] Unused CSS removed (PurgeCSS)
- [ ] CSS minified
- [ ] No @import statements
- [ ] Media queries for non-critical styles

```html
<!-- Critical CSS inline -->
<style>/* Critical styles */</style>

<!-- Non-critical async -->
<link rel="preload" href="styles.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
```

---

## Font Optimization

- [ ] System fonts or limited web fonts
- [ ] Fonts subset to used characters
- [ ] `font-display: swap` or `optional`
- [ ] Fonts preloaded
- [ ] WOFF2 format
- [ ] Fallback fonts match metrics

```html
<link rel="preload" href="font.woff2" as="font" type="font/woff2" crossorigin>
```

---

## Caching Strategy

- [ ] Static assets cached (1 year)
- [ ] HTML short cache or no-cache
- [ ] API responses cached appropriately
- [ ] Service worker caching strategy
- [ ] Cache busting via hashed filenames

```
# Example Cache-Control headers
Static assets: max-age=31536000, immutable
HTML: no-cache
API: max-age=60, stale-while-revalidate=3600
```

---

## Network Optimization

- [ ] HTTP/2 or HTTP/3 enabled
- [ ] Compression (Brotli → gzip)
- [ ] CDN for static assets
- [ ] DNS prefetch for external domains
- [ ] Preconnect to critical origins

```html
<link rel="dns-prefetch" href="//api.example.com">
<link rel="preconnect" href="https://fonts.googleapis.com" crossorigin>
```

---

## Mobile-Specific

- [ ] Touch interactions optimized
- [ ] Viewport configured correctly
- [ ] No horizontal scroll
- [ ] Works on slow 3G (3+ seconds)
- [ ] Offline mode handled gracefully
- [ ] Data saver mode respected

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

---

## Testing

### Tools
- [ ] Lighthouse (lab data)
- [ ] PageSpeed Insights (field data)
- [ ] WebPageTest
- [ ] Chrome DevTools Performance
- [ ] Real User Monitoring (RUM)

### Conditions
- [ ] Tested on 4G throttled
- [ ] Tested on 3G throttled
- [ ] Tested on real mobile device
- [ ] Tested on mid-range Android
- [ ] Tested with CPU throttling

---

## Monitoring

- [ ] Core Web Vitals tracked in analytics
- [ ] Performance budgets in CI/CD
- [ ] Alerts for regression
- [ ] Weekly performance review

---

## Results Summary

| Metric | Target | Mobile | Desktop | Status |
|--------|--------|--------|---------|--------|
| LCP | ≤2.5s | | | |
| INP | ≤200ms | | | |
| CLS | ≤0.1 | | | |
| FCP | ≤1.8s | | | |
| TTFB | ≤800ms | | | |
| Total Weight | ≤500KB | | | |
| Lighthouse | ≥90 | | | |

**Tested By:** _________________ **Date:** _________________
