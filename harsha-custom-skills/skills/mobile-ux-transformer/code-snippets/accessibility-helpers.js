/**
 * Accessibility Helpers
 * Utilities for mobile accessibility compliance
 */

// ==========================================================================
// Screen Reader Announcements
// ==========================================================================

const Announcer = {
  container: null,
  
  /**
   * Initialize the announcer container
   */
  init() {
    if (this.container) return;
    
    this.container = document.createElement('div');
    this.container.setAttribute('role', 'status');
    this.container.setAttribute('aria-live', 'polite');
    this.container.setAttribute('aria-atomic', 'true');
    this.container.className = 'sr-only';
    this.container.style.cssText = `
      position: absolute;
      width: 1px;
      height: 1px;
      padding: 0;
      margin: -1px;
      overflow: hidden;
      clip: rect(0, 0, 0, 0);
      white-space: nowrap;
      border: 0;
    `;
    document.body.appendChild(this.container);
  },
  
  /**
   * Announce a message to screen readers
   * @param {string} message
   * @param {'polite'|'assertive'} priority
   */
  announce(message, priority = 'polite') {
    this.init();
    
    this.container.setAttribute('aria-live', priority);
    
    // Clear and set message (triggers announcement)
    this.container.textContent = '';
    
    // Use setTimeout to ensure the DOM change is detected
    setTimeout(() => {
      this.container.textContent = message;
    }, 50);
    
    // Clear after announcement
    setTimeout(() => {
      this.container.textContent = '';
    }, 1000);
  },
  
  /**
   * Announce immediately (assertive)
   */
  announceNow(message) {
    this.announce(message, 'assertive');
  }
};

// ==========================================================================
// Focus Management
// ==========================================================================

const FocusManager = {
  /**
   * Get all focusable elements within a container
   */
  getFocusableElements(container = document) {
    const selector = [
      'a[href]',
      'button:not([disabled])',
      'input:not([disabled]):not([type="hidden"])',
      'select:not([disabled])',
      'textarea:not([disabled])',
      '[tabindex]:not([tabindex="-1"])',
      '[contenteditable="true"]'
    ].join(', ');
    
    return Array.from(container.querySelectorAll(selector))
      .filter(el => {
        // Check visibility
        const style = getComputedStyle(el);
        return style.display !== 'none' && 
               style.visibility !== 'hidden' &&
               el.offsetParent !== null;
      });
  },
  
  /**
   * Focus the first focusable element
   */
  focusFirst(container = document) {
    const elements = this.getFocusableElements(container);
    if (elements.length > 0) {
      elements[0].focus();
      return true;
    }
    return false;
  },
  
  /**
   * Focus the last focusable element
   */
  focusLast(container = document) {
    const elements = this.getFocusableElements(container);
    if (elements.length > 0) {
      elements[elements.length - 1].focus();
      return true;
    }
    return false;
  },
  
  /**
   * Save current focus for later restoration
   */
  saveFocus() {
    return document.activeElement;
  },
  
  /**
   * Restore previously saved focus
   */
  restoreFocus(element) {
    if (element && typeof element.focus === 'function') {
      element.focus();
    }
  }
};

// ==========================================================================
// Focus Trap (for modals, dialogs)
// ==========================================================================

class FocusTrap {
  constructor(element) {
    this.element = element;
    this.previousFocus = null;
    this.handleKeydown = this.handleKeydown.bind(this);
  }
  
  activate() {
    this.previousFocus = document.activeElement;
    
    document.addEventListener('keydown', this.handleKeydown);
    
    // Focus first element
    FocusManager.focusFirst(this.element);
    
    // Prevent focus outside trap
    this.element.addEventListener('focusout', (e) => {
      if (!this.element.contains(e.relatedTarget)) {
        FocusManager.focusFirst(this.element);
      }
    });
  }
  
  deactivate() {
    document.removeEventListener('keydown', this.handleKeydown);
    
    // Restore focus
    if (this.previousFocus) {
      this.previousFocus.focus();
    }
  }
  
  handleKeydown(e) {
    if (e.key !== 'Tab') return;
    
    const focusable = FocusManager.getFocusableElements(this.element);
    if (focusable.length === 0) return;
    
    const firstElement = focusable[0];
    const lastElement = focusable[focusable.length - 1];
    
    if (e.shiftKey) {
      // Shift + Tab
      if (document.activeElement === firstElement) {
        e.preventDefault();
        lastElement.focus();
      }
    } else {
      // Tab
      if (document.activeElement === lastElement) {
        e.preventDefault();
        firstElement.focus();
      }
    }
  }
}

// ==========================================================================
// Touch Target Validation
// ==========================================================================

const TouchTargetValidator = {
  MIN_SIZE: 44, // WCAG 2.2 recommended
  MIN_SIZE_AA: 24, // WCAG 2.2 AA minimum
  MIN_SPACING: 8,
  
  /**
   * Validate all interactive elements on the page
   */
  validate(minSize = this.MIN_SIZE) {
    const interactiveSelector = 'a, button, input, select, textarea, [role="button"], [tabindex]';
    const elements = document.querySelectorAll(interactiveSelector);
    const issues = [];
    
    elements.forEach(el => {
      const rect = el.getBoundingClientRect();
      
      // Check size
      if (rect.width < minSize || rect.height < minSize) {
        issues.push({
          element: el,
          type: 'size',
          width: rect.width,
          height: rect.height,
          required: minSize,
          selector: this.getSelector(el)
        });
      }
    });
    
    return issues;
  },
  
  /**
   * Get a CSS selector for an element
   */
  getSelector(el) {
    if (el.id) return `#${el.id}`;
    if (el.className) {
      const classes = el.className.split(' ').filter(c => c).slice(0, 2);
      return `.${classes.join('.')}`;
    }
    return el.tagName.toLowerCase();
  },
  
  /**
   * Highlight elements with issues (for debugging)
   */
  highlightIssues() {
    const issues = this.validate();
    
    issues.forEach(issue => {
      issue.element.style.outline = '3px solid red';
      issue.element.style.outlineOffset = '2px';
      issue.element.title = `Touch target too small: ${issue.width}×${issue.height}px (need ${issue.required}px)`;
    });
    
    return issues;
  }
};

// ==========================================================================
// Reduced Motion Helper
// ==========================================================================

const ReducedMotion = {
  /**
   * Check if user prefers reduced motion
   */
  prefersReduced() {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  },
  
  /**
   * Get appropriate animation duration
   */
  getDuration(normalDuration) {
    return this.prefersReduced() ? 0 : normalDuration;
  },
  
  /**
   * Apply animation only if motion is acceptable
   */
  animate(element, keyframes, options) {
    if (this.prefersReduced()) {
      // Apply end state immediately
      const endState = keyframes[keyframes.length - 1];
      Object.assign(element.style, endState);
      return null;
    }
    
    return element.animate(keyframes, options);
  },
  
  /**
   * Listen for preference changes
   */
  onChange(callback) {
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
    mq.addEventListener('change', (e) => callback(e.matches));
    return () => mq.removeEventListener('change', callback);
  }
};

// ==========================================================================
// Color Contrast Checker
// ==========================================================================

const ContrastChecker = {
  /**
   * Calculate contrast ratio between two colors
   * @param {string} color1 - Hex color
   * @param {string} color2 - Hex color
   * @returns {number} Contrast ratio
   */
  getContrastRatio(color1, color2) {
    const l1 = this.getRelativeLuminance(color1);
    const l2 = this.getRelativeLuminance(color2);
    const lighter = Math.max(l1, l2);
    const darker = Math.min(l1, l2);
    return (lighter + 0.05) / (darker + 0.05);
  },
  
  /**
   * Get relative luminance of a color
   */
  getRelativeLuminance(hex) {
    const rgb = this.hexToRgb(hex);
    const [r, g, b] = rgb.map(c => {
      c = c / 255;
      return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
  },
  
  /**
   * Convert hex to RGB
   */
  hexToRgb(hex) {
    hex = hex.replace('#', '');
    if (hex.length === 3) {
      hex = hex.split('').map(c => c + c).join('');
    }
    return [
      parseInt(hex.substr(0, 2), 16),
      parseInt(hex.substr(2, 2), 16),
      parseInt(hex.substr(4, 2), 16)
    ];
  },
  
  /**
   * Check if contrast meets WCAG requirements
   */
  meetsWCAG(ratio, level = 'AA', isLargeText = false) {
    if (level === 'AAA') {
      return isLargeText ? ratio >= 4.5 : ratio >= 7;
    }
    // AA
    return isLargeText ? ratio >= 3 : ratio >= 4.5;
  },
  
  /**
   * Get WCAG rating for a contrast ratio
   */
  getRating(ratio) {
    if (ratio >= 7) return 'AAA';
    if (ratio >= 4.5) return 'AA';
    if (ratio >= 3) return 'AA-large';
    return 'Fail';
  }
};

// ==========================================================================
// Skip Link Helper
// ==========================================================================

function createSkipLink(targetId = 'main-content', text = 'Skip to main content') {
  const skipLink = document.createElement('a');
  skipLink.href = `#${targetId}`;
  skipLink.className = 'skip-link';
  skipLink.textContent = text;
  skipLink.style.cssText = `
    position: absolute;
    top: -40px;
    left: 0;
    background: #000;
    color: #fff;
    padding: 8px 16px;
    z-index: 10000;
    transition: top 0.2s;
  `;
  
  skipLink.addEventListener('focus', () => {
    skipLink.style.top = '0';
  });
  
  skipLink.addEventListener('blur', () => {
    skipLink.style.top = '-40px';
  });
  
  document.body.insertBefore(skipLink, document.body.firstChild);
  
  return skipLink;
}

// ==========================================================================
// ARIA Helper
// ==========================================================================

const AriaHelper = {
  /**
   * Set loading state on an element
   */
  setLoading(element, isLoading) {
    element.setAttribute('aria-busy', isLoading.toString());
    if (isLoading) {
      element.setAttribute('aria-disabled', 'true');
    } else {
      element.removeAttribute('aria-disabled');
    }
  },
  
  /**
   * Set expanded state (for accordion, dropdown)
   */
  setExpanded(trigger, isExpanded) {
    trigger.setAttribute('aria-expanded', isExpanded.toString());
  },
  
  /**
   * Set selected state
   */
  setSelected(element, isSelected) {
    element.setAttribute('aria-selected', isSelected.toString());
  },
  
  /**
   * Set current page in navigation
   */
  setCurrent(element, type = 'page') {
    element.setAttribute('aria-current', type);
  },
  
  /**
   * Set invalid state on form field
   */
  setInvalid(field, errorMessage = null) {
    field.setAttribute('aria-invalid', 'true');
    
    if (errorMessage) {
      const errorId = `${field.id}-error`;
      let errorEl = document.getElementById(errorId);
      
      if (!errorEl) {
        errorEl = document.createElement('span');
        errorEl.id = errorId;
        errorEl.className = 'field-error';
        errorEl.setAttribute('role', 'alert');
        field.parentNode.appendChild(errorEl);
      }
      
      errorEl.textContent = errorMessage;
      
      const describedBy = field.getAttribute('aria-describedby') || '';
      if (!describedBy.includes(errorId)) {
        field.setAttribute('aria-describedby', `${describedBy} ${errorId}`.trim());
      }
    }
  },
  
  /**
   * Clear invalid state
   */
  clearInvalid(field) {
    field.removeAttribute('aria-invalid');
    
    const errorId = `${field.id}-error`;
    const errorEl = document.getElementById(errorId);
    if (errorEl) {
      errorEl.textContent = '';
    }
  }
};

// ==========================================================================
// Export
// ==========================================================================

export {
  Announcer,
  FocusManager,
  FocusTrap,
  TouchTargetValidator,
  ReducedMotion,
  ContrastChecker,
  createSkipLink,
  AriaHelper
};
