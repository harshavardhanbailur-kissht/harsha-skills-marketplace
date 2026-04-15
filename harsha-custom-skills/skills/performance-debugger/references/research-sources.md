# Research Sources & References (2025-2026)

Academic papers, industry resources, and documentation for performance optimization and debugging.

---

## 1. Google & Chrome Official

### Web Performance (web.dev)
- Rendering Performance fundamentals
- Core Web Vitals optimization (LCP, INP, CLS)
- RAIL performance model: Response <100ms, Animation <16ms, Idle <50ms, Load <1s
- Long Animation Frames (LoAF) API for frame performance monitoring

### Chrome DevTools
- Performance panel reference and recording
- Memory leak detection
- Layers panel for compositor debugging
- Long Tasks API and Scheduler API documentation

### Chrome Blog
- Hardware Accelerated Animations best practices
- scheduler.yield() origin trial and implementation
- Interaction to Next Paint (INP) as core metric

---

## 2. React Ecosystem

- **react.dev docs**: Profiler API, useMemo, useCallback, memo
- **React Compiler**: Automatic memoization (18.3+)
- **Server Components**: Shift computation from client to server
- **Streaming SSR**: Progressive HTML delivery for faster FCP/LCP

---

## 3. Three.js & WebGL

- **threejs.org manual**: Object disposal, performance optimization
- **pmndrs ecosystem**: drei (abstractions), postprocessing (effects), detect-gpu (capabilities)
- **OffscreenCanvas**: GPU rendering in Web Workers

---

## 4. Animation Libraries

- **GSAP**: Advanced timeline control, ScrollTrigger plugin
- **Framer Motion**: React-native motion library with Shared Layout
- **Lenis**: Smooth scroll library (works with GSAP ScrollTrigger)
- **Web Animations API**: Native browser animation spec

---

## 5. Core Web Vitals & RUM

- **web.dev/vitals**: Official CWV guides
- **Chrome User Experience Report (CrUX)**: Real user performance data via CrUX API
- **web-vitals library**: Production RUM measurement
- **Field vs Lab metrics**: Lab tools (Lighthouse) vs Field tools (CrUX)

---

## 6. Performance Tools (Lab & Field)

### Lab Tools
- Lighthouse: Automated auditing (CWV, best practices, accessibility)
- WebPageTest: Detailed waterfall, filmstrip, custom metrics
- DebugBear: Continuous performance monitoring
- SpeedCurve: Historical trending and competitive analysis

### Field Tools
- Chrome UX Report (CrUX): Real user data via BigQuery & CrUX API
- web-vitals library: Client-side RUM measurement
- Custom analytics: PerformanceObserver for production telemetry

---

## 7. Academic & Advanced Research

### Context-Aware Debugging (2024-2025)
- **LLMxCPG**: Code Property Graphs for 67-91% context reduction
- **RepairAgent**: Autonomous bug fixing (164 bugs on Defects4J)
- **ChatRepair**: Iterative refinement at $0.42/bug cost
- **UniDebugger/FixAgent**: 1.25-2.56× more bugs vs single-agent

### Code Quality
- **MuTAP**: 93.57% mutation score via mutation-guided testing
- **SWE-agent**: 90.5% edit success via linter guardrails

---

## 8. Industry & Community Sources

### Smashing Magazine
- CSS GPU Animation best practices
- Front-End Performance Checklist (annual)

### Evil Martians
- React Virtual DOM optimization
- Three.js + OffscreenCanvas for GPU offload

### CSS-Tricks / Kent C. Dodds
- Will-change property guidance
- useMemo vs useCallback decision tree

---

## 9. Browser APIs & Specs

### Performance Monitoring
- Performance Observer API (LoAF, longtask entries)
- Navigation Timing API
- User Timing API (mark/measure)
- Resource Timing API

### Scheduler & Responsiveness
- scheduler.yield() for main thread yielding
- scheduler.postTask() for priority scheduling
- isInputPending() to detect pending input

### Intersection & Resize Observers
- Lazy loading and visibility detection
- Adaptive quality based on container size

---

## 10. Business Impact & ROI

### Companies with Proven Results
- **Vodafone**: +8% sales (31% LCP improvement)
- **Tokopedia**: +23% session duration (55% LCP improvement)
- **Pinterest**: +15% SEO traffic (-40% wait time)
- **Rakuten**: +53.37% revenue per visitor (mobile optimization)

### Performance & Conversion Correlation
- -1s load time = -7% conversions
- LCP < 2.5s = +7% conversion rate
- All CWV passing = +8-15% search visibility

---

## Updated: February 2026

Sources span 2023-2026 research, ensuring current best practices for modern web performance, React 18+, Three.js r170+, and emerging browser APIs.
