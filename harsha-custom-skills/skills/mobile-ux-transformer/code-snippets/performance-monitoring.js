/**
 * Performance Monitoring
 * Core Web Vitals tracking and performance utilities
 */

// ==========================================================================
// Web Vitals Monitoring
// ==========================================================================

class WebVitalsMonitor {
  constructor(options = {}) {
    this.onReport = options.onReport || console.log;
    this.debug = options.debug || false;
    
    this.metrics = {
      LCP: null,
      INP: null,
      CLS: null,
      FCP: null,
      TTFB: null
    };
    
    this.init();
  }
  
  init() {
    this.observeLCP();
    this.observeCLS();
    this.observeFCP();
    this.observeTTFB();
    this.observeINP();
  }
  
  // Largest Contentful Paint
  observeLCP() {
    if (!('PerformanceObserver' in window)) return;
    
    try {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const lastEntry = entries[entries.length - 1];
        
        this.metrics.LCP = {
          value: lastEntry.startTime,
          rating: this.getRating('LCP', lastEntry.startTime),
          element: lastEntry.element?.tagName
        };
        
        if (this.debug) {
          console.log('LCP:', this.metrics.LCP);
        }
      });
      
      observer.observe({ type: 'largest-contentful-paint', buffered: true });
      
      // Report on page hide
      this.reportOnHide('LCP');
    } catch (e) {
      console.warn('LCP observation failed:', e);
    }
  }
  
  // Cumulative Layout Shift
  observeCLS() {
    if (!('PerformanceObserver' in window)) return;
    
    let clsValue = 0;
    let sessionValue = 0;
    let sessionEntries = [];
    
    try {
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (!entry.hadRecentInput) {
            const firstEntry = sessionEntries[0];
            const lastEntry = sessionEntries[sessionEntries.length - 1];
            
            // Start new session if gap > 1s or total > 5s
            if (sessionValue && 
                (entry.startTime - lastEntry.startTime > 1000 ||
                 entry.startTime - firstEntry.startTime > 5000)) {
              clsValue = Math.max(clsValue, sessionValue);
              sessionValue = 0;
              sessionEntries = [];
            }
            
            sessionEntries.push(entry);
            sessionValue += entry.value;
          }
        }
        
        clsValue = Math.max(clsValue, sessionValue);
        
        this.metrics.CLS = {
          value: clsValue,
          rating: this.getRating('CLS', clsValue)
        };
        
        if (this.debug) {
          console.log('CLS:', this.metrics.CLS);
        }
      });
      
      observer.observe({ type: 'layout-shift', buffered: true });
      this.reportOnHide('CLS');
    } catch (e) {
      console.warn('CLS observation failed:', e);
    }
  }
  
  // Interaction to Next Paint (INP)
  observeINP() {
    if (!('PerformanceObserver' in window)) return;
    
    const interactions = [];
    
    try {
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (entry.interactionId) {
            interactions.push(entry.duration);
          }
        }
        
        if (interactions.length > 0) {
          // INP is the 98th percentile
          interactions.sort((a, b) => b - a);
          const index = Math.min(interactions.length - 1, Math.floor(interactions.length / 50));
          const inp = interactions[index];
          
          this.metrics.INP = {
            value: inp,
            rating: this.getRating('INP', inp),
            interactionCount: interactions.length
          };
          
          if (this.debug) {
            console.log('INP:', this.metrics.INP);
          }
        }
      });
      
      observer.observe({ type: 'event', buffered: true, durationThreshold: 16 });
      this.reportOnHide('INP');
    } catch (e) {
      console.warn('INP observation failed:', e);
    }
  }
  
  // First Contentful Paint
  observeFCP() {
    if (!('PerformanceObserver' in window)) return;
    
    try {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntriesByName('first-contentful-paint');
        if (entries.length > 0) {
          this.metrics.FCP = {
            value: entries[0].startTime,
            rating: this.getRating('FCP', entries[0].startTime)
          };
          
          if (this.debug) {
            console.log('FCP:', this.metrics.FCP);
          }
        }
      });
      
      observer.observe({ type: 'paint', buffered: true });
    } catch (e) {
      console.warn('FCP observation failed:', e);
    }
  }
  
  // Time to First Byte
  observeTTFB() {
    if (!('PerformanceObserver' in window)) return;
    
    try {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntriesByType('navigation');
        if (entries.length > 0) {
          const nav = entries[0];
          const ttfb = nav.responseStart - nav.requestStart;
          
          this.metrics.TTFB = {
            value: ttfb,
            rating: this.getRating('TTFB', ttfb)
          };
          
          if (this.debug) {
            console.log('TTFB:', this.metrics.TTFB);
          }
        }
      });
      
      observer.observe({ type: 'navigation', buffered: true });
    } catch (e) {
      console.warn('TTFB observation failed:', e);
    }
  }
  
  // Rating thresholds (2024)
  getRating(metric, value) {
    const thresholds = {
      LCP: { good: 2500, poor: 4000 },
      INP: { good: 200, poor: 500 },
      CLS: { good: 0.1, poor: 0.25 },
      FCP: { good: 1800, poor: 3000 },
      TTFB: { good: 800, poor: 1800 }
    };
    
    const threshold = thresholds[metric];
    if (!threshold) return 'unknown';
    
    if (value <= threshold.good) return 'good';
    if (value <= threshold.poor) return 'needs-improvement';
    return 'poor';
  }
  
  reportOnHide(metric) {
    const reportMetric = () => {
      if (this.metrics[metric]) {
        this.onReport({
          name: metric,
          ...this.metrics[metric],
          timestamp: Date.now()
        });
      }
    };
    
    // Use visibilitychange for more reliable reporting
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'hidden') {
        reportMetric();
      }
    });
    
    // Fallback for pagehide
    window.addEventListener('pagehide', reportMetric);
  }
  
  // Get all current metrics
  getMetrics() {
    return { ...this.metrics };
  }
  
  // Report all metrics immediately
  reportAll() {
    Object.keys(this.metrics).forEach(metric => {
      if (this.metrics[metric]) {
        this.onReport({
          name: metric,
          ...this.metrics[metric],
          timestamp: Date.now()
        });
      }
    });
  }
}

// ==========================================================================
// Long Task Observer
// ==========================================================================

class LongTaskMonitor {
  constructor(options = {}) {
    this.threshold = options.threshold || 50; // ms
    this.onLongTask = options.onLongTask || console.warn;
    this.tasks = [];
    
    this.init();
  }
  
  init() {
    if (!('PerformanceObserver' in window)) return;
    
    try {
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          const task = {
            duration: entry.duration,
            startTime: entry.startTime,
            attribution: entry.attribution?.[0]?.containerType || 'unknown'
          };
          
          this.tasks.push(task);
          this.onLongTask(task);
        }
      });
      
      observer.observe({ type: 'longtask', buffered: true });
    } catch (e) {
      console.warn('Long task observation not supported');
    }
  }
  
  getTasks() {
    return [...this.tasks];
  }
  
  getTotalBlockingTime() {
    return this.tasks.reduce((total, task) => {
      return total + Math.max(0, task.duration - this.threshold);
    }, 0);
  }
}

// ==========================================================================
// Resource Timing
// ==========================================================================

class ResourceMonitor {
  static getResources(filter = {}) {
    const entries = performance.getEntriesByType('resource');
    
    return entries
      .filter(entry => {
        if (filter.type && !entry.initiatorType.includes(filter.type)) return false;
        if (filter.minDuration && entry.duration < filter.minDuration) return false;
        return true;
      })
      .map(entry => ({
        name: entry.name,
        type: entry.initiatorType,
        duration: entry.duration,
        size: entry.transferSize,
        cached: entry.transferSize === 0 && entry.decodedBodySize > 0
      }));
  }
  
  static getSlowestResources(count = 5) {
    return this.getResources()
      .sort((a, b) => b.duration - a.duration)
      .slice(0, count);
  }
  
  static getLargestResources(count = 5) {
    return this.getResources()
      .sort((a, b) => b.size - a.size)
      .slice(0, count);
  }
  
  static getTotalSize() {
    return this.getResources().reduce((total, r) => total + (r.size || 0), 0);
  }
  
  static getByType() {
    const resources = this.getResources();
    const byType = {};
    
    resources.forEach(r => {
      if (!byType[r.type]) {
        byType[r.type] = { count: 0, size: 0, duration: 0 };
      }
      byType[r.type].count++;
      byType[r.type].size += r.size || 0;
      byType[r.type].duration += r.duration;
    });
    
    return byType;
  }
}

// ==========================================================================
// Performance Budget Checker
// ==========================================================================

class PerformanceBudget {
  constructor(budgets = {}) {
    this.budgets = {
      // Time budgets (ms)
      LCP: 2500,
      INP: 200,
      FCP: 1800,
      TTFB: 800,
      
      // Size budgets (bytes)
      totalSize: 500 * 1024, // 500KB
      jsSize: 170 * 1024,    // 170KB
      cssSize: 50 * 1024,    // 50KB
      imageSize: 200 * 1024, // 200KB
      fontSize: 100 * 1024,  // 100KB
      
      // Count budgets
      requests: 50,
      jsRequests: 10,
      
      ...budgets
    };
  }
  
  check(metrics) {
    const results = [];
    
    // Time metrics
    if (metrics.LCP && metrics.LCP.value > this.budgets.LCP) {
      results.push({
        metric: 'LCP',
        budget: this.budgets.LCP,
        actual: metrics.LCP.value,
        overBy: metrics.LCP.value - this.budgets.LCP,
        passed: false
      });
    }
    
    if (metrics.INP && metrics.INP.value > this.budgets.INP) {
      results.push({
        metric: 'INP',
        budget: this.budgets.INP,
        actual: metrics.INP.value,
        overBy: metrics.INP.value - this.budgets.INP,
        passed: false
      });
    }
    
    // Resource sizes
    const resources = ResourceMonitor.getByType();
    const totalSize = ResourceMonitor.getTotalSize();
    
    if (totalSize > this.budgets.totalSize) {
      results.push({
        metric: 'totalSize',
        budget: this.budgets.totalSize,
        actual: totalSize,
        overBy: totalSize - this.budgets.totalSize,
        passed: false
      });
    }
    
    return {
      passed: results.length === 0,
      violations: results,
      summary: {
        totalChecks: Object.keys(this.budgets).length,
        violations: results.length
      }
    };
  }
}

// ==========================================================================
// Export
// ==========================================================================

export {
  WebVitalsMonitor,
  LongTaskMonitor,
  ResourceMonitor,
  PerformanceBudget
};

// Quick usage
export function initPerformanceMonitoring(options = {}) {
  const vitals = new WebVitalsMonitor({
    debug: options.debug,
    onReport: (metric) => {
      if (options.analytics) {
        // Send to analytics
        options.analytics.track('Web Vitals', {
          metric: metric.name,
          value: Math.round(metric.name === 'CLS' ? metric.value * 1000 : metric.value),
          rating: metric.rating
        });
      }
      
      if (options.onMetric) {
        options.onMetric(metric);
      }
    }
  });
  
  const longTasks = new LongTaskMonitor({
    onLongTask: (task) => {
      if (options.debug) {
        console.warn(`Long task: ${task.duration.toFixed(0)}ms`);
      }
    }
  });
  
  return { vitals, longTasks };
}
