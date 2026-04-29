# Case Study: Content Platform Mobile Transformation

> Optimizing a news/media platform for mobile reading and engagement

## Project Overview

| Attribute | Value |
|-----------|-------|
| **Client** | Digital news publisher |
| **Timeline** | 10 weeks |
| **Platform** | Responsive web + PWA |
| **Traffic Split** | 76% mobile, 24% desktop |
| **Problem** | Low engagement, high bounce rate, poor Core Web Vitals |

---

## Before: Desktop-Centric Content

### Identified Issues

1. **Reading Experience**
   - 14px body text (too small)
   - 75+ character line length on mobile
   - No dark mode support
   - Fixed header taking 15% of viewport

2. **Performance Crisis**
   - LCP: 6.2s (poor)
   - CLS: 0.45 (poor)
   - INP: 380ms (poor)
   - 15+ third-party scripts

3. **Navigation & Discovery**
   - Mega menu designed for hover
   - No bottom navigation
   - Related content below fold
   - Share buttons too small (28px)

4. **Advertising Issues**
   - Ads causing layout shifts
   - Interstitials blocking content
   - Auto-playing video ads
   - Sticky ads covering content

### Key Metrics (Before)

| Metric | Value |
|--------|-------|
| Average time on page | 47 seconds |
| Pages per session | 1.4 |
| Scroll depth (50%) | 34% |
| Social shares | 0.3% of pageviews |
| Return visitors | 18% |
| Core Web Vitals pass | 12% of pages |

---

## Mobile Transformation Strategy

### Phase 1: Typography & Reading Experience

**Typography System:**
```css
:root {
  /* Fluid type scale */
  --font-size-body: clamp(17px, 4vw, 20px);
  --font-size-h1: clamp(28px, 6vw, 48px);
  --font-size-h2: clamp(22px, 5vw, 32px);
  
  /* Optimal reading */
  --line-height-body: 1.65;
  --max-width-content: 65ch;
  
  /* Spacing */
  --paragraph-spacing: 1.5em;
}

/* Article body */
.article-body {
  font-size: var(--font-size-body);
  line-height: var(--line-height-body);
  max-width: var(--max-width-content);
  margin: 0 auto;
  padding: 0 20px;
}

.article-body p {
  margin-bottom: var(--paragraph-spacing);
}

/* Subheadings */
.article-body h2 {
  font-size: var(--font-size-h2);
  line-height: 1.25;
  margin-top: 2em;
  margin-bottom: 0.75em;
}
```

**Dark Mode Implementation:**
```css
@media (prefers-color-scheme: dark) {
  :root {
    --color-bg: #121212;
    --color-bg-elevated: #1e1e1e;
    --color-text: #e0e0e0;
    --color-text-secondary: #a0a0a0;
  }
}

/* Manual toggle support */
[data-theme="dark"] {
  --color-bg: #121212;
  --color-bg-elevated: #1e1e1e;
  --color-text: #e0e0e0;
  --color-text-secondary: #a0a0a0;
}

body {
  background-color: var(--color-bg);
  color: var(--color-text);
  transition: background-color 0.3s, color 0.3s;
}
```

### Phase 2: Performance Optimization

**Image Strategy:**
```html
<!-- Hero image with priority loading -->
<picture>
  <source 
    media="(max-width: 640px)" 
    srcset="hero-mobile.avif 1x, hero-mobile@2x.avif 2x"
    type="image/avif">
  <source 
    media="(max-width: 640px)" 
    srcset="hero-mobile.webp 1x, hero-mobile@2x.webp 2x"
    type="image/webp">
  <img 
    src="hero-desktop.jpg" 
    alt="Article hero image"
    width="800"
    height="450"
    fetchpriority="high"
    decoding="async">
</picture>

<!-- In-article images with lazy loading -->
<figure>
  <img 
    src="placeholder.svg"
    data-src="content-image.webp"
    alt="Descriptive alt text"
    width="600"
    height="400"
    loading="lazy"
    decoding="async"
    class="lazyload">
  <figcaption>Image caption</figcaption>
</figure>
```

**Script Optimization:**
```javascript
// Before: 15 scripts blocking render
// After: Critical only, rest deferred

// Critical (inline)
// - Analytics snippet
// - Above-fold functionality

// Deferred
const deferredScripts = [
  { src: '/js/comments.js', trigger: 'scroll' },
  { src: '/js/related.js', trigger: 'idle' },
  { src: '/js/social.js', trigger: 'interaction' }
];

// Load on interaction
document.addEventListener('scroll', () => {
  loadDeferredScripts('scroll');
}, { once: true, passive: true });

// Load when idle
if ('requestIdleCallback' in window) {
  requestIdleCallback(() => loadDeferredScripts('idle'));
}
```

**Ad Layout Stability:**
```css
/* Reserve space for ads */
.ad-slot {
  min-height: 250px;
  background: var(--color-bg-elevated);
  contain: layout style;
}

.ad-slot[data-size="mobile-banner"] {
  min-height: 100px;
  aspect-ratio: 320 / 100;
}

.ad-slot[data-size="mobile-rectangle"] {
  min-height: 250px;
  aspect-ratio: 300 / 250;
}
```

### Phase 3: Navigation & Engagement

**Collapsible Header:**
```javascript
class SmartHeader {
  constructor() {
    this.header = document.querySelector('.site-header');
    this.lastScroll = 0;
    this.threshold = 100;
    
    window.addEventListener('scroll', this.handleScroll.bind(this), { passive: true });
  }
  
  handleScroll() {
    const currentScroll = window.scrollY;
    
    if (currentScroll > this.threshold) {
      if (currentScroll > this.lastScroll) {
        // Scrolling down - hide header
        this.header.classList.add('header-hidden');
      } else {
        // Scrolling up - show header
        this.header.classList.remove('header-hidden');
      }
    }
    
    this.lastScroll = currentScroll;
  }
}
```

```css
.site-header {
  position: sticky;
  top: 0;
  transform: translateY(0);
  transition: transform 0.3s ease;
}

.site-header.header-hidden {
  transform: translateY(-100%);
}

/* Compact header on scroll */
.site-header.scrolled {
  padding: 8px 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
```

**Bottom Engagement Bar:**
```html
<div class="engagement-bar">
  <div class="progress-indicator">
    <div class="progress-fill" style="width: 45%"></div>
  </div>
  
  <div class="engagement-actions">
    <button class="action-btn" aria-label="Like article">
      <svg><!-- Heart --></svg>
      <span class="count">234</span>
    </button>
    
    <button class="action-btn" aria-label="Share article">
      <svg><!-- Share --></svg>
    </button>
    
    <button class="action-btn" aria-label="Save for later">
      <svg><!-- Bookmark --></svg>
    </button>
    
    <button class="action-btn" aria-label="Comments">
      <svg><!-- Comment --></svg>
      <span class="count">47</span>
    </button>
  </div>
</div>
```

```css
.engagement-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: var(--color-bg-elevated);
  border-top: 1px solid var(--color-border);
  padding: 8px 16px;
  padding-bottom: calc(8px + env(safe-area-inset-bottom));
  z-index: 100;
}

.progress-indicator {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--color-border);
}

.progress-fill {
  height: 100%;
  background: var(--color-primary);
  transition: width 0.1s linear;
}

.engagement-actions {
  display: flex;
  justify-content: space-around;
}

.action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  min-width: 48px;
  min-height: 44px;
  padding: 4px 8px;
  background: none;
  border: none;
  color: var(--color-text-secondary);
}

.action-btn:active {
  color: var(--color-primary);
  transform: scale(0.95);
}
```

### Phase 4: Reading Progress & Retention

**Reading Time Estimate:**
```javascript
function calculateReadingTime(text) {
  const wordsPerMinute = 200;
  const wordCount = text.trim().split(/\s+/).length;
  const minutes = Math.ceil(wordCount / wordsPerMinute);
  return minutes;
}

// Display
const readingTime = calculateReadingTime(articleText);
document.querySelector('.reading-time').textContent = 
  `${readingTime} min read`;
```

**"Continue Reading" for Return Visitors:**
```javascript
// Save scroll position
window.addEventListener('beforeunload', () => {
  const progress = window.scrollY / document.body.scrollHeight;
  if (progress > 0.1 && progress < 0.9) {
    localStorage.setItem(`article-${articleId}-progress`, progress);
  }
});

// Restore on return
document.addEventListener('DOMContentLoaded', () => {
  const savedProgress = localStorage.getItem(`article-${articleId}-progress`);
  if (savedProgress) {
    showContinueReadingPrompt(parseFloat(savedProgress));
  }
});

function showContinueReadingPrompt(progress) {
  const prompt = document.createElement('div');
  prompt.className = 'continue-prompt';
  prompt.innerHTML = `
    <p>Continue where you left off?</p>
    <button class="continue-btn">Continue Reading</button>
    <button class="dismiss-btn">Start Over</button>
  `;
  document.body.appendChild(prompt);
  
  prompt.querySelector('.continue-btn').addEventListener('click', () => {
    window.scrollTo({
      top: document.body.scrollHeight * progress,
      behavior: 'smooth'
    });
    prompt.remove();
  });
}
```

---

## After: Mobile-First Publishing

### Key Metrics (After)

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Time on page | 47s | 2m 34s | +228% |
| Pages per session | 1.4 | 2.8 | +100% |
| Scroll depth (50%) | 34% | 72% | +112% |
| Social shares | 0.3% | 1.8% | +500% |
| Return visitors | 18% | 41% | +128% |

### Core Web Vitals (After)

| Metric | Before | After | Status |
|--------|--------|-------|--------|
| LCP | 6.2s | 1.8s | ✅ Good |
| CLS | 0.45 | 0.04 | ✅ Good |
| INP | 380ms | 89ms | ✅ Good |
| CWV Pass Rate | 12% | 94% | ✅ Good |

### Engagement Improvements

| Feature | Impact |
|---------|--------|
| Bottom engagement bar | +340% shares |
| Dark mode | +23% evening sessions |
| Reading progress | +18% completion |
| Continue reading | +45% return engagement |

---

## Design Patterns Used

### 1. Fluid Typography
Responsive text that scales smoothly across devices.

### 2. Smart/Collapsing Header
Header hides on scroll down, reveals on scroll up.

### 3. Bottom Engagement Bar
Persistent actions for likes, shares, comments.

### 4. Reading Progress Indicator
Visual feedback on article completion.

### 5. Dark Mode Toggle
System preference + manual override.

---

## Key Learnings

1. **17-20px body text** — Optimal for mobile reading
2. **65ch max line width** — Improves readability significantly
3. **Hide header on scroll** — More content visible
4. **Bottom actions** — 340% more engagement than top
5. **Reserve ad space** — Critical for CLS
6. **Lazy load below fold** — Massive LCP improvement
7. **Dark mode matters** — 23% more evening usage
8. **Reading progress** — Increases completion rates

---

## Transformation Checklist Applied

- [x] 17-20px body text
- [x] 1.5+ line height
- [x] 65ch max line width
- [x] Dark mode support
- [x] Collapsing header
- [x] Bottom engagement bar
- [x] Reading progress indicator
- [x] LCP under 2.5s
- [x] CLS under 0.1
- [x] Reserved ad slots
- [x] Lazy loading images
- [x] Return visitor features
