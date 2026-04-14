# GSAP / Animation Bug Patterns

**Versions Covered:** GSAP 3.12.0+ through 3.14.2 (validated April 2, 2026)

### G-001: GSAP Context Not Cleaned Up

**Symptom:** Multiple tweens running simultaneously; animations conflict; memory grows

**Root Cause:** gsap.context() created but .revert() not called on component unmount

**Detection:**
```typescript
// BUGGY - no context cleanup
function AnimatedComponent() {
  useEffect(() => {
    gsap.context(() => {
      gsap.to('.box', { duration: 1, x: 100 });
    });
    // No cleanup - context persists
  }, []);
}
```

**Safe Fix (useGSAP Hook):**
```typescript
// Option 1: useGSAP hook (recommended)
import { useGSAP } from '@gsap/react';

function AnimatedComponent() {
  const containerRef = useRef(null);

  useGSAP(() => {
    gsap.to('.box', { duration: 1, x: 100 });
    gsap.to('.circle', { duration: 1, rotation: 360 });
  }, { scope: containerRef }); // Auto-cleanup on unmount

  return <div ref={containerRef}><div className="box" /><div className="circle" /></div>;
}

// Option 2: Manual cleanup
function AnimatedComponent() {
  const contextRef = useRef(null);

  useEffect(() => {
    contextRef.current = gsap.context(() => {
      gsap.to('.box', { duration: 1, x: 100 });
    });

    return () => {
      contextRef.current.revert(); // Must call revert()
    };
  }, []);
}
```

**UNSAFE Fix:**
```typescript
// DON'T: Store reference but forget to revert
function AnimatedComponent() {
  const ctx = gsap.context(() => {
    gsap.to('.box', { duration: 1, x: 100 });
  });

  useEffect(() => {
    return () => {
      // ctx.revert() is missing
    };
  }, []);
}
```

**Regression Test:**
```typescript
describe('G-001: GSAP Context Cleanup', () => {
  it('should revert context on unmount', () => {
    let context;

    function Component() {
      useGSAP(() => {
        gsap.to('.box', { x: 100 });
      }, { scope: containerRef });
    }

    const { unmount } = render(<Component />);
    unmount();

    // Verify tweens are killed
    expect(gsap.getTweensOf('.box')).toHaveLength(0);
  });
});
```

---

### G-002: ScrollTrigger Not Refreshed After DOM Change

**Symptom:** Scroll animations trigger at wrong scroll position after DOM updates

**Root Cause:** DOM content changes height but ScrollTrigger uses cached dimensions

**Detection:**
```typescript
// BUGGY - DOM changes but ScrollTrigger not updated
function Page() {
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    gsap.registerPlugin(ScrollTrigger);

    gsap.to('.section', {
      scrollTrigger: {
        trigger: '.section',
        start: 'top center'
      },
      duration: 1,
      y: 50
    });
  }, []);

  return (
    <>
      <div className="section" style={{ height: expanded ? 500 : 100 }}>
        {expanded && <div>More content...</div>}
      </div>
      <button onClick={() => setExpanded(!expanded)}>Expand</button>
    </>
  );
}
```

**Safe Fix:**
```typescript
function Page() {
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    gsap.registerPlugin(ScrollTrigger);

    gsap.to('.section', {
      scrollTrigger: {
        trigger: '.section',
        start: 'top center'
      },
      duration: 1,
      y: 50
    });
  }, []);

  // Refresh ScrollTrigger after DOM changes
  useEffect(() => {
    ScrollTrigger.refresh();
  }, [expanded]);

  return (
    <>
      <div className="section" style={{ height: expanded ? 500 : 100 }}>
        {expanded && <div>More content...</div>}
      </div>
      <button onClick={() => setExpanded(!expanded)}>Expand</button>
    </>
  );
}

// Better: Use useGSAP with dependencies
function Page() {
  const [expanded, setExpanded] = useState(false);
  const containerRef = useRef(null);

  useGSAP(() => {
    gsap.registerPlugin(ScrollTrigger);

    gsap.to('.section', {
      scrollTrigger: {
        trigger: '.section',
        start: 'top center',
        onUpdate: () => { /* ... */ }
      },
      y: 50
    });

    return () => ScrollTrigger.getAll().forEach(trigger => trigger.kill());
  }, { dependencies: [expanded], scope: containerRef });

  return (
    <div ref={containerRef}>
      <div className="section" style={{ height: expanded ? 500 : 100 }} />
      <button onClick={() => setExpanded(!expanded)}>Expand</button>
    </div>
  );
}
```

**UNSAFE Fix:**
```typescript
// DON'T: Call refresh without proper timing
function Page() {
  const [expanded, setExpanded] = useState(false);

  return (
    <>
      <div className="section" style={{ height: expanded ? 500 : 100 }} />
      <button onClick={() => {
        setExpanded(!expanded);
        ScrollTrigger.refresh(); // Timing wrong - DOM not updated yet
      }}>Expand</button>
    </>
  );
}
```

**Regression Test:**
```typescript
describe('G-002: ScrollTrigger Refresh', () => {
  it('should update trigger position on DOM change', async () => {
    const { rerender } = render(<Page />);

    const trigger1 = ScrollTrigger.getAll()[0];
    const start1 = trigger1.start;

    rerender(<Page expanded={true} />);
    ScrollTrigger.refresh();

    const trigger2 = ScrollTrigger.getAll()[0];
    const start2 = trigger2.start;

    expect(start2).not.toBe(start1); // Position changed
  });
});
```

---

### G-003: Lenis + ScrollTrigger Desync

**Symptom:** Scroll animations are jerky; scrollbar position doesn't match animation; animations skip

**Root Cause:** Lenis and ScrollTrigger use different scroll position sources; lagSmoothing conflicts

**Detection:**
```typescript
// BUGGY - Lenis and ScrollTrigger not synced
function App() {
  useEffect(() => {
    const lenis = new Lenis();

    gsap.registerPlugin(ScrollTrigger);

    gsap.to('.box', {
      scrollTrigger: {
        trigger: '.box',
        scrub: 1
      },
      x: 100
    });

    // Lenis updates scroll position but ScrollTrigger doesn't know
    lenis.on('scroll', () => {
      // ScrollTrigger not updated
    });
  }, []);
}
```

**Safe Fix:**
```typescript
function App() {
  useEffect(() => {
    const lenis = new Lenis();

    gsap.registerPlugin(ScrollTrigger);

    // Connect Lenis to ScrollTrigger
    lenis.on('scroll', ScrollTrigger.update);

    // Disable lagSmoothing for exact sync
    gsap.ticker.lagSmoothing(0);

    // Use gsap.ticker instead of requestAnimationFrame
    gsap.ticker.add((time) => {
      lenis.raf(time * 1000);
    });

    gsap.to('.box', {
      scrollTrigger: {
        trigger: '.box',
        scrub: 1
      },
      x: 100
    });

    return () => {
      lenis.destroy();
      ScrollTrigger.getAll().forEach(t => t.kill());
    };
  }, []);
}
```

**UNSAFE Fix:**
```typescript
// DON'T: Use both smooth scroll libraries without syncing
function App() {
  useEffect(() => {
    const lenis = new Lenis();

    // ScrollTrigger using native scroll
    gsap.registerPlugin(ScrollTrigger);
    gsap.to('.box', {
      scrollTrigger: { trigger: '.box', scrub: 1 },
      x: 100
    });

    // Lenis overrides scroll but ScrollTrigger doesn't update
  }, []);
}
```

**Regression Test:**
```typescript
describe('G-003: Lenis ScrollTrigger Sync', () => {
  it('should update ScrollTrigger on Lenis scroll', () => {
    const lenis = new Lenis();
    const updateSpy = jest.spyOn(ScrollTrigger, 'update');

    lenis.on('scroll', ScrollTrigger.update);
    lenis.scrollTo(500);

    expect(updateSpy).toHaveBeenCalled();
  });
});
```

---

### G-004: Conflicting Tweens

**Symptom:** Two animations animating same property fight each other; values jump or flicker

**Root Cause:** Multiple tweens animating the same property without killing previous tweens or setting overwrite

**Detection:**
```typescript
// BUGGY - conflicting tweens
function Button() {
  function handleHover() {
    gsap.to('.btn', { duration: 0.3, scale: 1.1 }); // Tween A
  }

  function handleClick() {
    gsap.to('.btn', { duration: 1, x: 100 }); // Tween B
    gsap.to('.btn', { duration: 1, scale: 1.2 }); // Tween C - conflicts with A!
  }

  return <button onMouseEnter={handleHover} onClick={handleClick}>Click me</button>;
}
```

**Safe Fix:**
```typescript
// Option 1: Kill previous tweens
function Button() {
  function handleHover() {
    gsap.killTweensOf('.btn'); // Kill all tweens
    gsap.to('.btn', { duration: 0.3, scale: 1.1 });
  }

  function handleClick() {
    gsap.killTweensOf('.btn'); // Kill all tweens
    gsap.to('.btn', { duration: 1, x: 100, scale: 1.2 });
  }

  return <button onMouseEnter={handleHover} onClick={handleClick}>Click me</button>;
}

// Option 2: Use overwrite option
function Button() {
  function handleHover() {
    gsap.to('.btn', {
      duration: 0.3,
      scale: 1.1,
      overwrite: 'auto' // Kill conflicting tweens automatically
    });
  }

  function handleClick() {
    gsap.to('.btn', {
      duration: 1,
      x: 100,
      scale: 1.2,
      overwrite: 'auto'
    });
  }

  return <button onMouseEnter={handleHover} onClick={handleClick}>Click me</button>;
}

// Option 3: Use timeline to manage animations
function Button() {
  const tlRef = useRef(gsap.timeline());

  function handleHover() {
    tlRef.current.clear();
    tlRef.current.to('.btn', { duration: 0.3, scale: 1.1 });
  }

  function handleClick() {
    tlRef.current.clear();
    tlRef.current.to('.btn', { duration: 1, x: 100, scale: 1.2 });
  }

  return <button onMouseEnter={handleHover} onClick={handleClick}>Click me</button>;
}
```

**UNSAFE Fix:**
```typescript
// DON'T: Ignore conflicting tweens
function Button() {
  function handleHover() {
    gsap.to('.btn', { duration: 0.3, scale: 1.1 });
  }

  function handleClick() {
    gsap.to('.btn', { duration: 1, x: 100, scale: 1.2 });
    // Two tweens modifying scale at different rates - values fight
  }
}
```

**Regression Test:**
```typescript
describe('G-004: Conflicting Tweens', () => {
  it('should kill previous tween on new animation', () => {
    const box = document.querySelector('.box');

    gsap.to(box, { duration: 1, x: 100 });
    expect(gsap.getTweensOf(box)).toHaveLength(1);

    gsap.killTweensOf(box);
    gsap.to(box, { duration: 0.5, scale: 1.5 });

    expect(gsap.getTweensOf(box)).toHaveLength(1); // Only new tween
  });
});
```

---
