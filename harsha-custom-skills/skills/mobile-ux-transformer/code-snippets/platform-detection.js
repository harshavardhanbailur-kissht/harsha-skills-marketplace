/**
 * Platform Detection
 * Detect device, OS, and browser for platform-specific adaptations
 */

const Platform = {
  // ==========================================================================
  // Operating System Detection
  // ==========================================================================
  
  isIOS() {
    return /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
  },
  
  isAndroid() {
    return /Android/.test(navigator.userAgent);
  },
  
  isWindows() {
    return /Windows/.test(navigator.userAgent);
  },
  
  isMac() {
    return /Mac/.test(navigator.userAgent) && !this.isIOS();
  },
  
  isLinux() {
    return /Linux/.test(navigator.userAgent) && !this.isAndroid();
  },
  
  // ==========================================================================
  // Device Type Detection
  // ==========================================================================
  
  isMobile() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
  },
  
  isTablet() {
    return /(tablet|ipad|playbook|silk)|(android(?!.*mobi))/i.test(navigator.userAgent);
  },
  
  isDesktop() {
    return !this.isMobile() && !this.isTablet();
  },
  
  isIPad() {
    return /iPad/.test(navigator.userAgent) || 
           (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
  },
  
  isIPhone() {
    return /iPhone/.test(navigator.userAgent);
  },
  
  // ==========================================================================
  // OS Version Detection
  // ==========================================================================
  
  getIOSVersion() {
    const match = navigator.userAgent.match(/OS (\d+)_(\d+)_?(\d+)?/);
    if (match) {
      return {
        major: parseInt(match[1], 10),
        minor: parseInt(match[2], 10),
        patch: parseInt(match[3] || 0, 10),
        full: `${match[1]}.${match[2]}${match[3] ? '.' + match[3] : ''}`
      };
    }
    return null;
  },
  
  getAndroidVersion() {
    const match = navigator.userAgent.match(/Android (\d+)\.?(\d+)?\.?(\d+)?/);
    if (match) {
      return {
        major: parseInt(match[1], 10),
        minor: parseInt(match[2] || 0, 10),
        patch: parseInt(match[3] || 0, 10),
        full: `${match[1]}${match[2] ? '.' + match[2] : ''}${match[3] ? '.' + match[3] : ''}`
      };
    }
    return null;
  },
  
  // ==========================================================================
  // Browser Detection
  // ==========================================================================
  
  isSafari() {
    return /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
  },
  
  isChrome() {
    return /Chrome/.test(navigator.userAgent) && !/Edg/.test(navigator.userAgent);
  },
  
  isFirefox() {
    return /Firefox/.test(navigator.userAgent);
  },
  
  isEdge() {
    return /Edg/.test(navigator.userAgent);
  },
  
  isSamsungBrowser() {
    return /SamsungBrowser/.test(navigator.userAgent);
  },
  
  // ==========================================================================
  // Feature Detection
  // ==========================================================================
  
  hasTouch() {
    return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
  },
  
  hasHover() {
    return window.matchMedia('(hover: hover)').matches;
  },
  
  hasFinePointer() {
    return window.matchMedia('(pointer: fine)').matches;
  },
  
  hasCoarsePointer() {
    return window.matchMedia('(pointer: coarse)').matches;
  },
  
  hasNotch() {
    // Check for safe area insets (indicates notch/dynamic island)
    const style = getComputedStyle(document.documentElement);
    const topInset = parseInt(style.getPropertyValue('--sat') || 
                             style.getPropertyValue('env(safe-area-inset-top)') || 0);
    return topInset > 20;
  },
  
  supportsVibration() {
    return 'vibrate' in navigator;
  },
  
  supportsWebGL() {
    try {
      const canvas = document.createElement('canvas');
      return !!(window.WebGLRenderingContext && 
                (canvas.getContext('webgl') || canvas.getContext('experimental-webgl')));
    } catch (e) {
      return false;
    }
  },
  
  supportsWebP() {
    const canvas = document.createElement('canvas');
    canvas.width = 1;
    canvas.height = 1;
    return canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0;
  },
  
  // ==========================================================================
  // Display Detection
  // ==========================================================================
  
  getPixelRatio() {
    return window.devicePixelRatio || 1;
  },
  
  isHighDensity() {
    return this.getPixelRatio() >= 2;
  },
  
  getScreenSize() {
    return {
      width: window.screen.width,
      height: window.screen.height,
      availWidth: window.screen.availWidth,
      availHeight: window.screen.availHeight
    };
  },
  
  getViewportSize() {
    return {
      width: window.innerWidth,
      height: window.innerHeight,
      visualViewportWidth: window.visualViewport?.width || window.innerWidth,
      visualViewportHeight: window.visualViewport?.height || window.innerHeight
    };
  },
  
  isLandscape() {
    return window.innerWidth > window.innerHeight;
  },
  
  isPortrait() {
    return window.innerHeight > window.innerWidth;
  },
  
  // ==========================================================================
  // User Preferences
  // ==========================================================================
  
  prefersReducedMotion() {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  },
  
  prefersDarkMode() {
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  },
  
  prefersHighContrast() {
    return window.matchMedia('(prefers-contrast: high)').matches;
  },
  
  // ==========================================================================
  // Connection Detection
  // ==========================================================================
  
  getConnectionType() {
    const connection = navigator.connection || 
                       navigator.mozConnection || 
                       navigator.webkitConnection;
    
    if (connection) {
      return {
        effectiveType: connection.effectiveType, // 'slow-2g', '2g', '3g', '4g'
        downlink: connection.downlink, // Mbps
        rtt: connection.rtt, // ms
        saveData: connection.saveData
      };
    }
    return null;
  },
  
  isSlowConnection() {
    const conn = this.getConnectionType();
    return conn && (conn.effectiveType === 'slow-2g' || conn.effectiveType === '2g');
  },
  
  // ==========================================================================
  // Standalone/PWA Detection
  // ==========================================================================
  
  isStandalone() {
    return window.matchMedia('(display-mode: standalone)').matches ||
           window.navigator.standalone === true;
  },
  
  isPWA() {
    return this.isStandalone();
  },
  
  // ==========================================================================
  // Comprehensive Platform Info
  // ==========================================================================
  
  getInfo() {
    const os = this.isIOS() ? 'iOS' :
               this.isAndroid() ? 'Android' :
               this.isMac() ? 'macOS' :
               this.isWindows() ? 'Windows' :
               this.isLinux() ? 'Linux' : 'Unknown';
    
    const osVersion = this.isIOS() ? this.getIOSVersion() :
                      this.isAndroid() ? this.getAndroidVersion() : null;
    
    const deviceType = this.isTablet() ? 'tablet' :
                       this.isMobile() ? 'mobile' : 'desktop';
    
    return {
      os,
      osVersion,
      deviceType,
      browser: {
        safari: this.isSafari(),
        chrome: this.isChrome(),
        firefox: this.isFirefox(),
        edge: this.isEdge(),
        samsung: this.isSamsungBrowser()
      },
      features: {
        touch: this.hasTouch(),
        hover: this.hasHover(),
        vibration: this.supportsVibration(),
        webgl: this.supportsWebGL(),
        webp: this.supportsWebP()
      },
      display: {
        pixelRatio: this.getPixelRatio(),
        viewport: this.getViewportSize(),
        orientation: this.isLandscape() ? 'landscape' : 'portrait'
      },
      preferences: {
        reducedMotion: this.prefersReducedMotion(),
        darkMode: this.prefersDarkMode(),
        highContrast: this.prefersHighContrast()
      },
      connection: this.getConnectionType(),
      standalone: this.isStandalone()
    };
  },
  
  // ==========================================================================
  // Apply Platform Classes
  // ==========================================================================
  
  applyClasses(element = document.documentElement) {
    const classes = [];
    
    // OS
    if (this.isIOS()) classes.push('os-ios');
    else if (this.isAndroid()) classes.push('os-android');
    else if (this.isMac()) classes.push('os-macos');
    else if (this.isWindows()) classes.push('os-windows');
    
    // Device type
    if (this.isMobile()) classes.push('device-mobile');
    if (this.isTablet()) classes.push('device-tablet');
    if (this.isDesktop()) classes.push('device-desktop');
    
    // Features
    if (this.hasTouch()) classes.push('has-touch');
    if (this.hasHover()) classes.push('has-hover');
    if (this.isHighDensity()) classes.push('high-density');
    
    // Preferences
    if (this.prefersReducedMotion()) classes.push('reduced-motion');
    if (this.prefersDarkMode()) classes.push('dark-mode');
    
    // Orientation
    classes.push(this.isLandscape() ? 'landscape' : 'portrait');
    
    // PWA
    if (this.isStandalone()) classes.push('standalone');
    
    // Apply classes
    element.classList.add(...classes);
    
    // Update orientation on change
    window.addEventListener('orientationchange', () => {
      element.classList.remove('landscape', 'portrait');
      element.classList.add(this.isLandscape() ? 'landscape' : 'portrait');
    });
    
    return classes;
  }
};

// ==========================================================================
// Export
// ==========================================================================

export default Platform;

// Auto-apply classes when DOM is ready
if (typeof document !== 'undefined') {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => Platform.applyClasses());
  } else {
    Platform.applyClasses();
  }
}
