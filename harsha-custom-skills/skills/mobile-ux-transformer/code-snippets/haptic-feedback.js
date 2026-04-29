/**
 * Haptic Feedback
 * Cross-platform haptic feedback utilities
 */

const HapticFeedback = {
  // Check if vibration is supported
  isSupported: typeof navigator !== 'undefined' && 'vibrate' in navigator,
  
  // User preference (can be toggled)
  enabled: true,
  
  // ==========================================================================
  // Haptic Patterns (duration in milliseconds)
  // ==========================================================================
  
  patterns: {
    // Impact feedback
    light: 10,
    medium: 20,
    heavy: 30,
    
    // Selection
    selection: 5,
    tick: 5,
    
    // Notifications
    success: [10, 50, 10, 50, 20],
    warning: [20, 100, 20],
    error: [50, 100, 50, 100, 50],
    
    // UI interactions
    tap: 10,
    doubleTap: [10, 50, 10],
    longPress: 20,
    
    // Gestures
    swipe: 15,
    dragStart: 15,
    dragMove: 5,
    drop: 20,
    
    // Other
    toggle: 15,
    slider: 5,
    refresh: [10, 50, 20]
  },
  
  // ==========================================================================
  // Core Methods
  // ==========================================================================
  
  /**
   * Trigger haptic feedback
   * @param {string|number|number[]} pattern - Pattern name, duration, or array
   */
  trigger(pattern = 'light') {
    if (!this.isSupported || !this.enabled) return false;
    
    let vibrationPattern;
    
    if (typeof pattern === 'string') {
      vibrationPattern = this.patterns[pattern] || this.patterns.light;
    } else {
      vibrationPattern = pattern;
    }
    
    try {
      return navigator.vibrate(vibrationPattern);
    } catch (e) {
      console.warn('Haptic feedback failed:', e);
      return false;
    }
  },
  
  /**
   * Stop any ongoing vibration
   */
  stop() {
    if (this.isSupported) {
      navigator.vibrate(0);
    }
  },
  
  // ==========================================================================
  // Semantic Methods
  // ==========================================================================
  
  /**
   * Impact feedback (for button taps, etc.)
   * @param {'light'|'medium'|'heavy'} style
   */
  impact(style = 'medium') {
    return this.trigger(style);
  },
  
  /**
   * Selection feedback (for picker changes, sliders)
   */
  selection() {
    return this.trigger('selection');
  },
  
  /**
   * Notification feedback
   * @param {'success'|'warning'|'error'} type
   */
  notification(type = 'success') {
    return this.trigger(type);
  },
  
  // ==========================================================================
  // UI Interaction Methods
  // ==========================================================================
  
  /** Button tap */
  tap() {
    return this.trigger('tap');
  },
  
  /** Long press activated */
  longPress() {
    return this.trigger('longPress');
  },
  
  /** Toggle switch */
  toggle() {
    return this.trigger('toggle');
  },
  
  /** Swipe action completed */
  swipe() {
    return this.trigger('swipe');
  },
  
  /** Drag started */
  dragStart() {
    return this.trigger('dragStart');
  },
  
  /** Item dropped/reordered */
  drop() {
    return this.trigger('drop');
  },
  
  /** Slider value changed */
  slider() {
    return this.trigger('slider');
  },
  
  /** Refresh completed */
  refresh() {
    return this.trigger('refresh');
  },
  
  // ==========================================================================
  // Settings
  // ==========================================================================
  
  /**
   * Enable or disable haptics
   * @param {boolean} enabled
   */
  setEnabled(enabled) {
    this.enabled = enabled;
    
    // Persist preference
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem('haptics-enabled', enabled.toString());
    }
  },
  
  /**
   * Load user preference from storage
   */
  loadPreference() {
    if (typeof localStorage !== 'undefined') {
      const pref = localStorage.getItem('haptics-enabled');
      if (pref !== null) {
        this.enabled = pref === 'true';
      }
    }
  },
  
  // ==========================================================================
  // Custom Patterns
  // ==========================================================================
  
  /**
   * Add or override a pattern
   * @param {string} name
   * @param {number|number[]} pattern
   */
  addPattern(name, pattern) {
    this.patterns[name] = pattern;
  },
  
  /**
   * Create a custom haptic sequence
   * @param {Array<{pattern: string, delay?: number}>} sequence
   */
  async sequence(steps) {
    for (const step of steps) {
      this.trigger(step.pattern);
      if (step.delay) {
        await new Promise(resolve => setTimeout(resolve, step.delay));
      }
    }
  }
};

// Load saved preference on init
HapticFeedback.loadPreference();

// ==========================================================================
// React Hook (if React is available)
// ==========================================================================

/**
 * React hook for haptic feedback
 * Usage: const haptics = useHaptics();
 *        haptics.tap();
 */
function useHaptics() {
  return HapticFeedback;
}

// ==========================================================================
// Vue Directive (if Vue is available)
// ==========================================================================

/**
 * Vue directive for haptic feedback
 * Usage: <button v-haptic="'tap'">Click</button>
 *        <button v-haptic:long-press>Hold</button>
 */
const vHaptic = {
  mounted(el, binding) {
    const pattern = binding.arg?.replace(/-/g, '') || binding.value || 'tap';
    
    el.addEventListener('click', () => {
      HapticFeedback.trigger(pattern);
    });
    
    if (pattern === 'longPress' || pattern === 'longpress') {
      let timer;
      el.addEventListener('touchstart', () => {
        timer = setTimeout(() => {
          HapticFeedback.longPress();
        }, 500);
      });
      el.addEventListener('touchend', () => clearTimeout(timer));
      el.addEventListener('touchcancel', () => clearTimeout(timer));
    }
  }
};

// ==========================================================================
// Auto-bind to common elements
// ==========================================================================

/**
 * Automatically add haptic feedback to interactive elements
 * @param {HTMLElement} root - Root element to search within
 */
function autoBindHaptics(root = document) {
  // Buttons
  root.querySelectorAll('button, [role="button"]').forEach(el => {
    if (!el.dataset.hapticBound) {
      el.addEventListener('click', () => HapticFeedback.tap());
      el.dataset.hapticBound = 'true';
    }
  });
  
  // Toggles/Switches
  root.querySelectorAll('input[type="checkbox"], [role="switch"]').forEach(el => {
    if (!el.dataset.hapticBound) {
      el.addEventListener('change', () => HapticFeedback.toggle());
      el.dataset.hapticBound = 'true';
    }
  });
  
  // Range sliders
  root.querySelectorAll('input[type="range"]').forEach(el => {
    if (!el.dataset.hapticBound) {
      let lastValue = el.value;
      el.addEventListener('input', () => {
        if (el.value !== lastValue) {
          HapticFeedback.slider();
          lastValue = el.value;
        }
      });
      el.dataset.hapticBound = 'true';
    }
  });
}

// ==========================================================================
// Export
// ==========================================================================

export default HapticFeedback;
export { useHaptics, vHaptic, autoBindHaptics };
