# Case Study: Content Site Mobile Optimization

> Transforming a news/media site for mobile-first reading

## Overview

**Client:** Digital media publisher
**Timeline:** 6 weeks
**Mobile Traffic:** 72% of total
**Core Web Vitals (Before):** 18% passing
**Core Web Vitals (After):** 94% passing
**Ad Revenue Impact:** +28% mobile RPM

---

## The Problem

### Performance Issues
- LCP: 6.8 seconds (target: 2.5s)
- CLS: 0.42 (target: 0.1)
- INP: 380ms (target: 200ms)
- Only 18% of mobile pages passing Core Web Vitals

### User Experience Issues
- Intrusive interstitial ads
- Layout shifts from late-loading ads
- Tiny text requiring zoom
- Infinite scroll causing scroll hijacking
- No offline reading capability

### Business Impact
- High bounce rate: 71%
- Low pages per session: 1.4
- Poor ad viewability: 38%
- SEO rankings declining

---

## Transformation Process

### Phase 1: Performance Foundation (Weeks 1-2)

#### LCP Optimization

**Problem:** Hero images loading slowly, render-blocking CSS

**Solution:**
```html
<!-- Preload LCP image -->
<link rel="preload" as="image" href="hero-mobile.webp" 
      media="(max-width: 768px)"
      fetchpriority="high">

<!-- Critical CSS inline -->
<style>
  /* Only above-fold styles - ~12KB */
  .article-header { ... }
  .hero-image { ... }
  .article-lead { ... }
</style>

<!-- Non-critical CSS async -->
<link rel="preload" href="styles.css" as="style" 
      onload="this.onload=null;this.rel='stylesheet'">
```

**Image optimization:**
```html
<picture>
  <source 
    srcset="hero-400.avif 400w, hero-800.avif 800w"
    sizes="100vw"
    type="image/avif">
  <source 
    srcset="hero-400.webp 400w, hero-800.webp 800w"
    sizes="100vw"
    type="image/webp">
  <img 
    src="hero-800.jpg"
    alt="Article hero image"
    width="800"
    height="450"
    loading="eager"
    fetchpriority="high"
    decoding="async">
</picture>
```

**Results:** LCP 6.8s → 2.1s

#### CLS Fixes

**Problem:** Ads and images causing layout shifts

**Solution:**
```css
/* Reserve space for ads */
.ad-slot {
  min-height: 250px; /* Standard mobile ad height */
  background: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ad-slot::before {
  content: 'Advertisement';
  font-size: 10px;
  color: #999;
  text-transform: uppercase;
}

/* Aspect ratio for images */
.article-image {
  aspect-ratio: 16 / 9;
  width: 100%;
  object-fit: cover;
  background: #eee;
}

/* Font loading without shift */
@font-face {
  font-family: 'Article Font';
  src: url('font.woff2') format('woff2');
  font-display: swap;
  /* Size-adjust to match fallback */
  size-adjust: 105%;
  ascent-override: 95%;
}

body {
  font-family: 'Article Font', Georgia, serif;
}
```

**Results:** CLS 0.42 → 0.06

#### INP Optimization

**Problem:** Heavy JavaScript blocking interactions

**Solution:**
```javascript
// Break up long tasks
async function processArticle() {
  // Yield to browser between chunks
  await yieldToMain();
  renderHeader();
  
  await yieldToMain();
  renderBody();
  
  await yieldToMain();
  initAds();
}

function yieldToMain() {
  return new Promise(resolve => {
    if ('scheduler' in window) {
      scheduler.yield().then(resolve);
    } else {
      setTimeout(resolve, 0);
    }
  });
}

// Defer non-critical scripts
<script src="analytics.js" defer></script>
<script src="social-share.js" defer></script>
<script src="comments.js" type="module" async></script>
```

**Results:** INP 380ms → 145ms

### Phase 2: Reading Experience (Weeks 3-4)

#### Typography Optimization

```css
/* Mobile-optimized reading */
.article-body {
  font-size: 18px;
  line-height: 1.7;
  max-width: 100%;
  padding: 0 16px;
}

/* Optimal line length */
@media (min-width: 600px) {
  .article-body {
    max-width: 65ch;
    margin: 0 auto;
    padding: 0 24px;
  }
}

/* Better paragraph spacing */
.article-body p {
  margin-bottom: 1.5em;
}

/* Pull quotes */
.pull-quote {
  font-size: 24px;
  font-style: italic;
  border-left: 4px solid var(--primary);
  padding-left: 16px;
  margin: 32px 0;
}

/* Image captions */
.figure-caption {
  font-size: 14px;
  color: #666;
  margin-top: 8px;
  font-style: italic;
}
```

#### Reading Progress Indicator

```html
<div class="reading-progress" aria-hidden="true">
  <div class="progress-bar"></div>
</div>
```

```css
.reading-progress {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: rgba(0,0,0,0.1);
  z-index: 1000;
}

.progress-bar {
  height: 100%;
  background: var(--primary);
  width: 0%;
  transition: width 0.1s;
}
```

```javascript
window.addEventListener('scroll', () => {
  const article = document.querySelector('.article-body');
  const rect = article.getBoundingClientRect();
  const progress = Math.min(1, Math.max(0, 
    -rect.top / (rect.height - window.innerHeight)
  ));
  document.querySelector('.progress-bar').style.width = `${progress * 100}%`;
}, { passive: true });
```

#### Estimated Reading Time

```javascript
function getReadingTime(text) {
  const wordsPerMinute = 200;
  const words = text.trim().split(/\s+/).length;
  const minutes = Math.ceil(words / wordsPerMinute);
  return `${minutes} min read`;
}
```

```html
<div class="article-meta">
  <time datetime="2024-01-15">Jan 15, 2024</time>
  <span class="reading-time">5 min read</span>
</div>
```

### Phase 3: Ad Experience (Week 5)

#### Better Ad Placements

**Before:** Interstitials, pop-ups, content-shifting ads
**After:** Native-style, reserved-space, non-intrusive

```html
<!-- In-article native ad -->
<aside class="native-ad" aria-label="Sponsored content">
  <span class="ad-label">Sponsored</span>
  <a href="/sponsored/..." class="native-ad-link">
    <img src="sponsor-thumb.webp" alt="" width="100" height="100" loading="lazy">
    <div class="native-ad-content">
      <h4>Sponsor Headline</h4>
      <p>Brief description of sponsored content...</p>
    </div>
  </a>
</aside>
```

```css
.native-ad {
  background: #f9f9f9;
  border-radius: 8px;
  padding: 16px;
  margin: 32px 0;
}

.ad-label {
  font-size: 10px;
  text-transform: uppercase;
  color: #999;
  letter-spacing: 0.5px;
}

.native-ad-link {
  display: flex;
  gap: 12px;
  text-decoration: none;
  color: inherit;
  margin-top: 8px;
}
```

#### Lazy-load Ads Below Fold

```javascript
// Intersection Observer for ad loading
const adObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      loadAd(entry.target);
      adObserver.unobserve(entry.target);
    }
  });
}, {
  rootMargin: '200px' // Load slightly before visible
});

document.querySelectorAll('.ad-slot[data-lazy]').forEach(slot => {
  adObserver.observe(slot);
});
```

### Phase 4: Navigation & Discovery (Week 6)

#### Sticky Header (Minimal)

```css
.site-header {
  position: sticky;
  top: 0;
  background: white;
  z-index: 100;
  transform: translateY(0);
  transition: transform 0.3s;
}

.site-header.hidden {
  transform: translateY(-100%);
}
```

```javascript
// Hide on scroll down, show on scroll up
let lastScroll = 0;
window.addEventListener('scroll', () => {
  const currentScroll = window.scrollY;
  const header = document.querySelector('.site-header');
  
  if (currentScroll > lastScroll && currentScroll > 100) {
    header.classList.add('hidden');
  } else {
    header.classList.remove('hidden');
  }
  
  lastScroll = currentScroll;
}, { passive: true });
```

#### Related Articles

```html
<section class="related-articles" aria-labelledby="related-heading">
  <h2 id="related-heading">More to Read</h2>
  
  <div class="article-cards">
    <a href="/article-2" class="article-card">
      <img src="thumb.webp" alt="" width="120" height="80" loading="lazy">
      <div class="card-content">
        <h3>Related Article Title</h3>
        <span class="meta">3 min read</span>
      </div>
    </a>
    <!-- More cards -->
  </div>
</section>
```

#### Offline Reading (PWA)

```javascript
// Service worker caching for articles
self.addEventListener('fetch', (event) => {
  if (event.request.url.includes('/article/')) {
    event.respondWith(
      caches.match(event.request).then(response => {
        return response || fetch(event.request).then(fetchResponse => {
          const responseClone = fetchResponse.clone();
          caches.open('articles-v1').then(cache => {
            cache.put(event.request, responseClone);
          });
          return fetchResponse;
        });
      })
    );
  }
});
```

```html
<!-- Save for offline button -->
<button class="save-offline" aria-label="Save for offline reading">
  <svg><!-- Download icon --></svg>
  Save
</button>
```

---

## Results

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| LCP | 6.8s | 2.1s | -69% |
| CLS | 0.42 | 0.06 | -86% |
| INP | 380ms | 145ms | -62% |
| Core Web Vitals Pass | 18% | 94% | +422% |
| Bounce Rate | 71% | 48% | -32% |
| Pages/Session | 1.4 | 2.3 | +64% |
| Ad Viewability | 38% | 72% | +89% |
| Mobile RPM | $4.20 | $5.38 | +28% |
| SEO Ranking | Declining | Top 10 | Improved |

---

## Key Learnings

1. **Performance = Revenue** — Faster pages = better ad viewability = higher RPM
2. **Reserve ad space** — Eliminates CLS, improves UX and viewability
3. **Typography matters** — Readable text = longer sessions
4. **Native ads work** — Less intrusive, higher engagement
5. **PWA adds value** — Offline reading increases loyalty

---

## Technical Stack

- **CMS:** Headless WordPress + Next.js
- **CDN:** Cloudflare with auto-minification
- **Images:** Cloudinary with auto-format
- **Ads:** Google Ad Manager with lazy loading
- **Analytics:** Google Analytics 4 + Core Web Vitals tracking
- **PWA:** Workbox for service worker
