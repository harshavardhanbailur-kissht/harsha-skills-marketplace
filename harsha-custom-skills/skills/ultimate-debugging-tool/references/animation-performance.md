# Animation Performance Reference Guide

**Core Principle**: NEVER suggest removing intentional animations. Optimize HOW they run instead.

## 1. GSAP Performance (3.12+)

### Proxy Pattern for Three.js (REQUIRED)
Never flag as overhead—enables efficient 3D updates without re-renders.

```javascript
gsap.registerPlugin(ScrollTrigger);

// CORRECT: Proxy pattern
gsap.to(meshRef.current.rotation, {
  z: Math.PI * 2,
  duration: 3,
  scrollTrigger: {
    trigger: containerRef.current,
    start: "top center",
    markers: false
  }
});

// PROXY for Three.js updates (REQUIRED FOR PERFORMANCE)
gsap.to({}, {
  onUpdate: function() {
    meshRef.current.position.x = this.targets()[0].value;
  },
  duration: 2
});
```

### ScrollTrigger Optimization
```javascript
// CORRECT: Batch creation + lazy initialization
const triggers = gsap.utils.toArray('[data-scroll]').map(el => ({
  trigger: el,
  onEnter: () => gsap.to(el, { opacity: 1, duration: 0.6 }),
  once: true
}));

// Lazy initialization
ScrollTrigger.batch('[data-scroll]', {
  onEnter: batch => gsap.to(batch, { opacity: 1, duration: 0.6 }),
  onLeave: batch => gsap.to(batch, { opacity: 0, duration: 0.3 }),
  interval: 100
});

// CRITICAL: manage refresh() carefully
window.addEventListener('resize', () => {
  setTimeout(() => ScrollTrigger.refresh(), 100);
});
```

### lagSmoothing(0) for Three.js/Lenis
**REQUIRED**—never disable. Prevents jank with high-refresh displays.

```javascript
gsap.ticker.lagSmoothing(0);

// Integration with Lenis
const lenis = new Lenis({ lerp: 0.05 });
gsap.ticker.add((time) => {
  lenis.raf(time * 1000);
});
```

### React Cleanup with gsap.context()
**CRITICAL** to prevent memory leaks.

```javascript
// CORRECT
useEffect(() => {
  const ctx = gsap.context(() => {
    gsap.to('.box', { rotation: 360, duration: 2 });
    gsap.to('.text', { opacity: 0.5, duration: 1 });
  }, containerRef);

  return () => ctx.revert(); // Kills ALL tweens, clears ScrollTriggers
}, []);

// WRONG: tweens persist on unmount
useEffect(() => {
  gsap.to('.box', { rotation: 360, duration: 2 }); // MEMORY LEAK
}, []);
```

### Timeline Orchestration
Overlapping with `-=` is intentional, not wasteful.

```javascript
const tl = gsap.timeline();
tl.to('.item1', { x: 100, duration: 1 })
  .to('.item2', { x: 100, duration: 1 }, '-=0.5') // Overlaps 0.5s
  .to('.item3', { opacity: 1, duration: 0.6 }, 0); // Parallel
```

---

## 2. Framer Motion Performance (v11+)

### Layout Animation Cost
One-time measure via FLIP technique—efficient by design.

```javascript
// SAFE: Layout recalculation only when layout prop present
<motion.div layout>
  {children}
</motion.div>

// Flag if causing measured jank: use layoutId + layoutDependency
<motion.div layout layoutId="item" layoutDependency={items.length}>
  {item.name}
</motion.div>
```

### Motion Values vs State
Motion values are CHEAPER (no re-render).

```javascript
// BETTER: Motion value, no re-render
const x = useMotionValue(0);
useEffect(() => {
  const unsubscribe = x.onChange(v => {
    console.log('Position:', v);
  });
  return unsubscribe;
}, [x]);

// AVOID: State re-renders component
const [x, setX] = useState(0);
const animate = () => setX(100); // Triggers re-render
```

### AnimatePresence Exit Animations
DOM retention for exit is expected behavior, not a bug.

```javascript
<AnimatePresence mode="wait">
  {isVisible && (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.3 }}
    >
      Content
    </motion.div>
  )}
</AnimatePresence>
```

---

## 3. CSS Animation Performance

### Composite-Only Properties (SAFE)
```css
/* SAFE: No layout recalculation */
.box {
  animation: slide 2s ease-in-out;
}
@keyframes slide {
  from { transform: translateX(0); }
  to { transform: translateX(100px); }
}

/* SAFE: Opacity */
@keyframes fade {
  from { opacity: 1; }
  to { opacity: 0; }
}

/* SAFE: Filter */
@keyframes blur-in {
  from { filter: blur(10px); }
  to { filter: blur(0); }
}
```

### Layout-Triggering Properties (ALWAYS FLAG)
```css
/* WRONG: Triggers layout recalculation */
@keyframes slide-bad {
  from { left: 0; } /* BAD: reflow every frame */
  to { left: 100px; }
}

/* WRONG: Animating width */
@keyframes expand {
  from { width: 0; } /* BAD: layout shift */
  to { width: 200px; }
}
```

**Fix**: Use `transform: scaleX()` or `max-width` with transition (for content).

### will-change Lifecycle
```css
/* ADD before animation */
.box {
  will-change: transform, opacity;
}

/* REMOVE after (don't leave persistent) */
.box.animated {
  will-change: auto; /* Important cleanup */
}
```

### CSS contain & content-visibility
```css
/* Isolate animation to subtree */
.animated-section {
  contain: layout style paint;
}

/* Skip rendering offscreen elements */
.offscreen {
  content-visibility: auto;
}
```

### View Transitions API (2025-2026 stable)
```javascript
// Page/route transitions
async function navigate(url) {
  if (!document.startViewTransition) {
    window.location.href = url;
    return;
  }

  document.startViewTransition(() => {
    updateDOM(url); // Update synchronously
  });
}

/* CSS side */
::view-transition-old(root) {
  animation: slide-out 0.3s ease-in;
}
::view-transition-new(root) {
  animation: slide-in 0.3s ease-out;
}
```

### CSS scroll-driven animations (Efficient, no JS)
```css
.element {
  animation: slide linear;
  animation-timeline: view();
  animation-range: entry 0% cover 50%;
}

@keyframes slide {
  from { transform: translateX(-100px); }
  to { transform: translateX(100px); }
}
```

---

## 4. Lenis Smooth Scroll

**Never flag as "unnecessary overhead"**—it's a deliberate UX choice.

```javascript
// CORRECT: Continuous lerp interpolation (0.05-0.15)
const lenis = new Lenis({
  lerp: 0.08, // INTENTIONAL smoothing
  wheelMultiplier: 1.2
});

// Integration with GSAP ticker
gsap.ticker.add((time) => {
  lenis.raf(time * 1000);
});

// Route cleanup + recreate
useEffect(() => {
  const lenis = new Lenis();
  gsap.ticker.add((time) => lenis.raf(time * 1000));

  return () => {
    lenis.destroy();
    gsap.ticker.remove(lenis.raf);
  };
}, []);

// iOS Safari fix (if needed)
<div className="lenis-wrapper" style={{ overflow: 'hidden' }}>
  <div className="lenis-content">{children}</div>
</div>
```

---

## 5. Web Animations API (WAAPI)

Native, compositor-thread when possible.

```javascript
// SAFE: Browser-native performance
const animation = element.animate(
  [
    { transform: 'translateX(0)', opacity: 1 },
    { transform: 'translateX(100px)', opacity: 0.5 }
  ],
  {
    duration: 2000,
    easing: 'ease-in-out',
    composite: 'accumulate'
  }
);

// Lifecycle management
animation.ready.then(() => console.log('Started'));
animation.finished.then(() => console.log('Done'));
```

---

## 6. Detection Patterns (Context-Aware)

### Pattern 1: Layout Property Animation
```javascript
// DETECT
/animation.*?(width|height|top|left|margin|padding):/
// OR in code: gsap.to(el, { width: '200px' })

// CHECK: Is this intentional? (search for max-width transition)
// FIX:
gsap.to(el, { scaleX: 1.5, transformOrigin: 'left', duration: 1 });

// TIER: Aggressive
```

### Pattern 2: will-change without cleanup
```javascript
// DETECT
/will-change:.*?(?!auto|none)/
// Missing removal on animation end

// FIX:
useEffect(() => {
  el.style.willChange = 'transform, opacity';
  const anim = gsap.to(el, { duration: 2, onComplete: () => {
    el.style.willChange = 'auto';
  } });
  return () => anim.kill();
}, []);

// TIER: Moderate
```

### Pattern 3: Scroll handler without RAF
```javascript
// DETECT
/addEventListener\(['"]scroll['"]\s*,\s*[^}]*(?!requestAnimationFrame)/

// FIX:
let ticking = false;
window.addEventListener('scroll', () => {
  if (!ticking) {
    requestAnimationFrame(() => {
      // Update animation
      ticking = false;
    });
    ticking = true;
  }
}, { passive: true });

// TIER: Always flag
```

### Pattern 4: Missing prefers-reduced-motion
```javascript
// DETECT
/@keyframes|animation:|transition:/
// WITHOUT @media (prefers-reduced-motion)

// FIX:
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}

// TIER: Always flag
```

### Pattern 5: Animation in useEffect without cleanup
```javascript
// DETECT
/useEffect\(\(\).*?gsap\.to\(/
// WITHOUT gsap.context or return kill

// FIX:
useEffect(() => {
  const ctx = gsap.context(() => {
    gsap.to('.item', { duration: 1, rotation: 360 });
  });
  return () => ctx.revert();
}, []);

// TIER: Aggressive
```

### Pattern 6: setTimeout/setInterval for animation
```javascript
// DETECT
/(setTimeout|setInterval)\(.*?\d+\)/
// used for animation timing

// FIX:
gsap.delayedCall(0.5, () => {
  gsap.to('.item', { opacity: 1, duration: 1 });
});

// TIER: Always flag
```

---

## Summary Table

| Issue | Trigger | Safe Fix | Tier |
|-------|---------|----------|------|
| Layout properties | `width`, `height`, `left`, `top` | `transform`, `scale` | Aggressive |
| will-change persistent | No cleanup after animation | Add `willChange: 'auto'` on complete | Moderate |
| Scroll without RAF | Direct scroll listener | Wrap in RAF + `passive: true` | Always |
| No reduced motion | Missing `@media` query | Add prefers-reduced-motion fallback | Always |
| Unmount memory leak | No context cleanup (React) | Wrap in `gsap.context()` | Aggressive |
| setTimeout animation | Timer-based frame updates | Use GSAP ticker or RAF | Always |
