/**
 * Gesture Handlers
 * Touch gesture detection and handling utilities
 */

// ==========================================================================
// Tap Handler
// ==========================================================================

class TapHandler {
  constructor(element, callback, options = {}) {
    this.element = element;
    this.callback = callback;
    this.maxDuration = options.maxDuration || 300;
    this.maxDistance = options.maxDistance || 10;
    
    this.startX = 0;
    this.startY = 0;
    this.startTime = 0;
    
    this.handleStart = this.handleStart.bind(this);
    this.handleEnd = this.handleEnd.bind(this);
    
    element.addEventListener('touchstart', this.handleStart, { passive: true });
    element.addEventListener('touchend', this.handleEnd);
  }
  
  handleStart(e) {
    this.startX = e.touches[0].clientX;
    this.startY = e.touches[0].clientY;
    this.startTime = Date.now();
  }
  
  handleEnd(e) {
    const duration = Date.now() - this.startTime;
    const endX = e.changedTouches[0].clientX;
    const endY = e.changedTouches[0].clientY;
    const distance = Math.hypot(endX - this.startX, endY - this.startY);
    
    if (duration < this.maxDuration && distance < this.maxDistance) {
      this.callback(e);
    }
  }
  
  destroy() {
    this.element.removeEventListener('touchstart', this.handleStart);
    this.element.removeEventListener('touchend', this.handleEnd);
  }
}

// ==========================================================================
// Long Press Handler
// ==========================================================================

class LongPressHandler {
  constructor(element, callback, options = {}) {
    this.element = element;
    this.callback = callback;
    this.duration = options.duration || 500;
    this.maxDistance = options.maxDistance || 10;
    
    this.timer = null;
    this.triggered = false;
    this.startX = 0;
    this.startY = 0;
    
    this.handleStart = this.handleStart.bind(this);
    this.handleMove = this.handleMove.bind(this);
    this.handleEnd = this.handleEnd.bind(this);
    
    element.addEventListener('touchstart', this.handleStart, { passive: true });
    element.addEventListener('touchmove', this.handleMove, { passive: true });
    element.addEventListener('touchend', this.handleEnd);
    element.addEventListener('touchcancel', this.handleEnd);
  }
  
  handleStart(e) {
    this.triggered = false;
    this.startX = e.touches[0].clientX;
    this.startY = e.touches[0].clientY;
    
    this.timer = setTimeout(() => {
      this.triggered = true;
      
      // Haptic feedback
      if (navigator.vibrate) {
        navigator.vibrate(20);
      }
      
      this.callback(e);
    }, this.duration);
  }
  
  handleMove(e) {
    const moveX = e.touches[0].clientX;
    const moveY = e.touches[0].clientY;
    const distance = Math.hypot(moveX - this.startX, moveY - this.startY);
    
    if (distance > this.maxDistance) {
      this.cancel();
    }
  }
  
  handleEnd() {
    this.cancel();
  }
  
  cancel() {
    clearTimeout(this.timer);
  }
  
  destroy() {
    this.cancel();
    this.element.removeEventListener('touchstart', this.handleStart);
    this.element.removeEventListener('touchmove', this.handleMove);
    this.element.removeEventListener('touchend', this.handleEnd);
    this.element.removeEventListener('touchcancel', this.handleEnd);
  }
}

// ==========================================================================
// Swipe Handler
// ==========================================================================

class SwipeHandler {
  constructor(element, callbacks, options = {}) {
    this.element = element;
    this.callbacks = callbacks; // { left, right, up, down }
    this.minDistance = options.minDistance || 50;
    this.maxDuration = options.maxDuration || 300;
    
    this.startX = 0;
    this.startY = 0;
    this.startTime = 0;
    
    this.handleStart = this.handleStart.bind(this);
    this.handleEnd = this.handleEnd.bind(this);
    
    element.addEventListener('touchstart', this.handleStart, { passive: true });
    element.addEventListener('touchend', this.handleEnd);
  }
  
  handleStart(e) {
    this.startX = e.touches[0].clientX;
    this.startY = e.touches[0].clientY;
    this.startTime = Date.now();
  }
  
  handleEnd(e) {
    const duration = Date.now() - this.startTime;
    if (duration > this.maxDuration) return;
    
    const endX = e.changedTouches[0].clientX;
    const endY = e.changedTouches[0].clientY;
    
    const deltaX = endX - this.startX;
    const deltaY = endY - this.startY;
    const absX = Math.abs(deltaX);
    const absY = Math.abs(deltaY);
    
    // Horizontal swipe
    if (absX > absY && absX > this.minDistance) {
      if (deltaX > 0 && this.callbacks.right) {
        this.callbacks.right(e, deltaX);
      } else if (deltaX < 0 && this.callbacks.left) {
        this.callbacks.left(e, Math.abs(deltaX));
      }
    }
    // Vertical swipe
    else if (absY > absX && absY > this.minDistance) {
      if (deltaY > 0 && this.callbacks.down) {
        this.callbacks.down(e, deltaY);
      } else if (deltaY < 0 && this.callbacks.up) {
        this.callbacks.up(e, Math.abs(deltaY));
      }
    }
  }
  
  destroy() {
    this.element.removeEventListener('touchstart', this.handleStart);
    this.element.removeEventListener('touchend', this.handleEnd);
  }
}

// ==========================================================================
// Swipe-to-Reveal Actions
// ==========================================================================

class SwipeActions {
  constructor(element, options = {}) {
    this.element = element;
    this.content = element.querySelector(options.contentSelector || '.swipe-content');
    this.actions = element.querySelector(options.actionsSelector || '.swipe-actions');
    this.actionsWidth = options.actionsWidth || 80;
    this.threshold = options.threshold || 40;
    this.onAction = options.onAction || (() => {});
    
    this.currentX = 0;
    this.startX = 0;
    this.isDragging = false;
    this.isOpen = false;
    
    this.handleStart = this.handleStart.bind(this);
    this.handleMove = this.handleMove.bind(this);
    this.handleEnd = this.handleEnd.bind(this);
    
    element.addEventListener('touchstart', this.handleStart, { passive: true });
    element.addEventListener('touchmove', this.handleMove, { passive: false });
    element.addEventListener('touchend', this.handleEnd);
  }
  
  handleStart(e) {
    this.startX = e.touches[0].clientX;
    this.currentX = this.isOpen ? -this.actionsWidth : 0;
    this.isDragging = true;
    this.content.style.transition = 'none';
  }
  
  handleMove(e) {
    if (!this.isDragging) return;
    
    const deltaX = e.touches[0].clientX - this.startX;
    let newX = this.currentX + deltaX;
    
    // Constrain movement
    newX = Math.max(-this.actionsWidth, Math.min(0, newX));
    
    // Add resistance at edges
    if (newX < -this.actionsWidth) {
      newX = -this.actionsWidth + (newX + this.actionsWidth) * 0.3;
    }
    
    this.content.style.transform = `translateX(${newX}px)`;
    
    // Prevent scroll if swiping
    if (Math.abs(deltaX) > 10) {
      e.preventDefault();
    }
  }
  
  handleEnd(e) {
    if (!this.isDragging) return;
    this.isDragging = false;
    
    this.content.style.transition = 'transform 0.2s ease-out';
    
    const deltaX = e.changedTouches[0].clientX - this.startX;
    
    if (this.isOpen) {
      if (deltaX > this.threshold) {
        this.close();
      } else {
        this.open();
      }
    } else {
      if (deltaX < -this.threshold) {
        this.open();
      } else {
        this.close();
      }
    }
  }
  
  open() {
    this.isOpen = true;
    this.content.style.transform = `translateX(-${this.actionsWidth}px)`;
    
    if (navigator.vibrate) {
      navigator.vibrate(10);
    }
  }
  
  close() {
    this.isOpen = false;
    this.content.style.transform = 'translateX(0)';
  }
  
  destroy() {
    this.element.removeEventListener('touchstart', this.handleStart);
    this.element.removeEventListener('touchmove', this.handleMove);
    this.element.removeEventListener('touchend', this.handleEnd);
  }
}

// ==========================================================================
// Pull-to-Refresh
// ==========================================================================

class PullToRefresh {
  constructor(options) {
    this.container = options.container;
    this.onRefresh = options.onRefresh;
    this.threshold = options.threshold || 80;
    this.resistance = options.resistance || 2.5;
    
    this.startY = 0;
    this.currentY = 0;
    this.isPulling = false;
    this.isRefreshing = false;
    
    this.createIndicator();
    this.setupEventListeners();
  }
  
  createIndicator() {
    this.indicator = document.createElement('div');
    this.indicator.className = 'pull-indicator';
    this.indicator.innerHTML = `
      <div class="pull-arrow">↓</div>
      <div class="pull-text">Pull to refresh</div>
      <div class="pull-spinner" hidden>
        <svg viewBox="0 0 24 24" width="24" height="24">
          <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="2" stroke-dasharray="31.4 31.4" transform="rotate(-90 12 12)">
            <animateTransform attributeName="transform" type="rotate" from="0 12 12" to="360 12 12" dur="1s" repeatCount="indefinite"/>
          </circle>
        </svg>
      </div>
    `;
    this.indicator.style.cssText = `
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 60px;
      display: flex;
      align-items: center;
      justify-content: center;
      transform: translateY(-100%);
      transition: transform 0.2s;
    `;
    this.container.style.position = 'relative';
    this.container.insertBefore(this.indicator, this.container.firstChild);
  }
  
  setupEventListeners() {
    this.handleStart = this.handleStart.bind(this);
    this.handleMove = this.handleMove.bind(this);
    this.handleEnd = this.handleEnd.bind(this);
    
    this.container.addEventListener('touchstart', this.handleStart, { passive: true });
    this.container.addEventListener('touchmove', this.handleMove, { passive: false });
    this.container.addEventListener('touchend', this.handleEnd);
  }
  
  handleStart(e) {
    if (this.isRefreshing) return;
    if (this.container.scrollTop > 0) return;
    
    this.startY = e.touches[0].clientY;
    this.isPulling = true;
  }
  
  handleMove(e) {
    if (!this.isPulling) return;
    
    this.currentY = e.touches[0].clientY;
    let pullDistance = (this.currentY - this.startY) / this.resistance;
    pullDistance = Math.min(pullDistance, this.threshold * 1.5);
    
    if (pullDistance > 0) {
      e.preventDefault();
      this.indicator.style.transform = `translateY(${pullDistance - 60}px)`;
      
      if (pullDistance >= this.threshold) {
        this.indicator.querySelector('.pull-text').textContent = 'Release to refresh';
        this.indicator.classList.add('ready');
      } else {
        this.indicator.querySelector('.pull-text').textContent = 'Pull to refresh';
        this.indicator.classList.remove('ready');
      }
    }
  }
  
  async handleEnd() {
    if (!this.isPulling) return;
    this.isPulling = false;
    
    const pullDistance = (this.currentY - this.startY) / this.resistance;
    
    if (pullDistance >= this.threshold && !this.isRefreshing) {
      this.isRefreshing = true;
      
      // Show spinner
      this.indicator.querySelector('.pull-arrow').hidden = true;
      this.indicator.querySelector('.pull-text').hidden = true;
      this.indicator.querySelector('.pull-spinner').hidden = false;
      this.indicator.style.transform = 'translateY(0)';
      
      // Haptic feedback
      if (navigator.vibrate) {
        navigator.vibrate(20);
      }
      
      try {
        await this.onRefresh();
      } finally {
        this.isRefreshing = false;
        
        // Reset indicator
        this.indicator.querySelector('.pull-arrow').hidden = false;
        this.indicator.querySelector('.pull-text').hidden = false;
        this.indicator.querySelector('.pull-spinner').hidden = true;
        this.indicator.style.transform = 'translateY(-100%)';
        this.indicator.classList.remove('ready');
      }
    } else {
      this.indicator.style.transform = 'translateY(-100%)';
      this.indicator.classList.remove('ready');
    }
  }
  
  destroy() {
    this.container.removeEventListener('touchstart', this.handleStart);
    this.container.removeEventListener('touchmove', this.handleMove);
    this.container.removeEventListener('touchend', this.handleEnd);
    this.indicator.remove();
  }
}

// ==========================================================================
// Pinch-to-Zoom
// ==========================================================================

class PinchZoom {
  constructor(element, options = {}) {
    this.element = element;
    this.minScale = options.minScale || 1;
    this.maxScale = options.maxScale || 4;
    this.onScale = options.onScale || (() => {});
    
    this.scale = 1;
    this.initialDistance = 0;
    this.initialScale = 1;
    
    this.handleStart = this.handleStart.bind(this);
    this.handleMove = this.handleMove.bind(this);
    this.handleEnd = this.handleEnd.bind(this);
    
    element.addEventListener('touchstart', this.handleStart, { passive: false });
    element.addEventListener('touchmove', this.handleMove, { passive: false });
    element.addEventListener('touchend', this.handleEnd);
  }
  
  getDistance(touches) {
    return Math.hypot(
      touches[0].clientX - touches[1].clientX,
      touches[0].clientY - touches[1].clientY
    );
  }
  
  handleStart(e) {
    if (e.touches.length === 2) {
      e.preventDefault();
      this.initialDistance = this.getDistance(e.touches);
      this.initialScale = this.scale;
    }
  }
  
  handleMove(e) {
    if (e.touches.length === 2) {
      e.preventDefault();
      const currentDistance = this.getDistance(e.touches);
      const scaleChange = currentDistance / this.initialDistance;
      this.scale = Math.min(this.maxScale, Math.max(this.minScale, this.initialScale * scaleChange));
      
      this.element.style.transform = `scale(${this.scale})`;
      this.onScale(this.scale);
    }
  }
  
  handleEnd() {
    this.initialDistance = 0;
  }
  
  reset() {
    this.scale = 1;
    this.element.style.transform = 'scale(1)';
  }
  
  destroy() {
    this.element.removeEventListener('touchstart', this.handleStart);
    this.element.removeEventListener('touchmove', this.handleMove);
    this.element.removeEventListener('touchend', this.handleEnd);
  }
}

// ==========================================================================
// Export
// ==========================================================================

export {
  TapHandler,
  LongPressHandler,
  SwipeHandler,
  SwipeActions,
  PullToRefresh,
  PinchZoom
};
