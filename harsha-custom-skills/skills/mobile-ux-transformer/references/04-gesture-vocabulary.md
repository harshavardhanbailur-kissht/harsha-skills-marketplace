# Gesture Vocabulary

> Standard touch interactions with platform-specific considerations

## Universal Touch Gestures

### Primary Gestures

| Gesture | Action | Common Uses |
|---------|--------|-------------|
| **Tap** | Single touch and release | Select, activate, open |
| **Double-tap** | Two quick taps | Zoom, like/favorite, select word |
| **Long-press** | Touch and hold (500ms+) | Context menu, drag mode, preview |
| **Swipe** | Touch, drag, release | Scroll, navigate, reveal actions |
| **Drag** | Touch, hold, move | Reorder, move, select range |
| **Pinch** | Two fingers together/apart | Zoom in/out |
| **Rotate** | Two fingers rotating | Rotate content |

### Gesture Parameters

| Parameter | Standard Value | Notes |
|-----------|---------------|-------|
| Tap duration | <300ms | Longer = long-press |
| Long-press threshold | 500ms | Platform varies (400-800ms) |
| Double-tap interval | <300ms | Between taps |
| Swipe velocity | >0.5 px/ms | Distinguishes from scroll |
| Pinch threshold | >10px movement | Before zoom activates |

---

## Platform-Specific Gestures

### iOS System Gestures

| Gesture | Location | Action |
|---------|----------|--------|
| Swipe from left edge | Left screen edge | Back navigation |
| Swipe from bottom | Bottom edge | Home / App switcher |
| Swipe down from top-left | Top-left corner | Notification Center |
| Swipe down from top-right | Top-right corner | Control Center |
| Two-finger swipe down | Status bar | Quick settings |
| Three-finger swipe | Anywhere | Copy/Paste/Undo |
| Pinch with five fingers | Anywhere | Home screen |

### Android System Gestures

| Gesture | Location | Action |
|---------|----------|--------|
| Swipe from left/right edge | Screen edges | Back (gesture nav) |
| Swipe up from bottom | Bottom edge | Home |
| Swipe up and hold | Bottom edge | Recent apps |
| Swipe down from top | Top edge | Notification shade |
| Swipe down twice from top | Top edge | Quick settings |
| Back button | Navigation bar | Back (3-button nav) |

### Avoiding System Gesture Conflicts

```css
/* iOS: Respect safe areas for edge gestures */
.content {
  padding-left: env(safe-area-inset-left);
  padding-right: env(safe-area-inset-right);
}

/* Android: Add padding from edges for swipe gestures */
.swipeable-item {
  margin-left: 24px; /* Avoid back gesture zone */
}

/* Disable user scaling on gesture-heavy areas */
.gesture-area {
  touch-action: none;
}
```

---

## Gesture Implementation Patterns

### Tap Handler

```javascript
class TapHandler {
  constructor(element, callback) {
    this.element = element;
    this.callback = callback;
    this.startX = 0;
    this.startY = 0;
    this.startTime = 0;
    
    this.element.addEventListener('touchstart', this.onStart.bind(this));
    this.element.addEventListener('touchend', this.onEnd.bind(this));
  }
  
  onStart(e) {
    this.startX = e.touches[0].clientX;
    this.startY = e.touches[0].clientY;
    this.startTime = Date.now();
  }
  
  onEnd(e) {
    const duration = Date.now() - this.startTime;
    const endX = e.changedTouches[0].clientX;
    const endY = e.changedTouches[0].clientY;
    const distance = Math.hypot(endX - this.startX, endY - this.startY);
    
    // Valid tap: short duration, minimal movement
    if (duration < 300 && distance < 10) {
      this.callback(e);
    }
  }
}
```

### Long-Press Handler

```javascript
class LongPressHandler {
  constructor(element, callback, duration = 500) {
    this.element = element;
    this.callback = callback;
    this.duration = duration;
    this.timer = null;
    this.triggered = false;
    
    this.element.addEventListener('touchstart', this.onStart.bind(this));
    this.element.addEventListener('touchmove', this.onMove.bind(this));
    this.element.addEventListener('touchend', this.onEnd.bind(this));
    this.element.addEventListener('touchcancel', this.onEnd.bind(this));
  }
  
  onStart(e) {
    this.triggered = false;
    this.startX = e.touches[0].clientX;
    this.startY = e.touches[0].clientY;
    
    this.timer = setTimeout(() => {
      this.triggered = true;
      
      // Haptic feedback
      if (navigator.vibrate) {
        navigator.vibrate(10);
      }
      
      this.callback(e);
    }, this.duration);
  }
  
  onMove(e) {
    const moveX = e.touches[0].clientX;
    const moveY = e.touches[0].clientY;
    const distance = Math.hypot(moveX - this.startX, moveY - this.startY);
    
    // Cancel if moved too much
    if (distance > 10) {
      this.cancel();
    }
  }
  
  onEnd() {
    this.cancel();
  }
  
  cancel() {
    clearTimeout(this.timer);
  }
}
```

### Swipe Handler

```javascript
class SwipeHandler {
  constructor(element, callbacks) {
    this.element = element;
    this.callbacks = callbacks; // { left, right, up, down }
    this.startX = 0;
    this.startY = 0;
    this.startTime = 0;
    
    this.element.addEventListener('touchstart', this.onStart.bind(this));
    this.element.addEventListener('touchend', this.onEnd.bind(this));
  }
  
  onStart(e) {
    this.startX = e.touches[0].clientX;
    this.startY = e.touches[0].clientY;
    this.startTime = Date.now();
  }
  
  onEnd(e) {
    const endX = e.changedTouches[0].clientX;
    const endY = e.changedTouches[0].clientY;
    const duration = Date.now() - this.startTime;
    
    const deltaX = endX - this.startX;
    const deltaY = endY - this.startY;
    const absX = Math.abs(deltaX);
    const absY = Math.abs(deltaY);
    
    // Minimum distance and velocity
    const minDistance = 50;
    const maxDuration = 300;
    
    if (duration > maxDuration) return;
    
    // Determine direction
    if (absX > absY && absX > minDistance) {
      if (deltaX > 0 && this.callbacks.right) {
        this.callbacks.right(e);
      } else if (deltaX < 0 && this.callbacks.left) {
        this.callbacks.left(e);
      }
    } else if (absY > absX && absY > minDistance) {
      if (deltaY > 0 && this.callbacks.down) {
        this.callbacks.down(e);
      } else if (deltaY < 0 && this.callbacks.up) {
        this.callbacks.up(e);
      }
    }
  }
}
```

### Swipe-to-Reveal Actions

```javascript
class SwipeActions {
  constructor(element, options) {
    this.element = element;
    this.content = element.querySelector('.swipe-content');
    this.actions = element.querySelector('.swipe-actions');
    this.actionsWidth = options.actionsWidth || 80;
    this.threshold = options.threshold || 40;
    
    this.currentX = 0;
    this.startX = 0;
    this.isDragging = false;
    this.isOpen = false;
    
    this.setupTouchHandlers();
  }
  
  setupTouchHandlers() {
    this.element.addEventListener('touchstart', this.onStart.bind(this));
    this.element.addEventListener('touchmove', this.onMove.bind(this));
    this.element.addEventListener('touchend', this.onEnd.bind(this));
  }
  
  onStart(e) {
    this.startX = e.touches[0].clientX;
    this.currentX = this.isOpen ? -this.actionsWidth : 0;
    this.isDragging = true;
    this.content.style.transition = 'none';
  }
  
  onMove(e) {
    if (!this.isDragging) return;
    
    const deltaX = e.touches[0].clientX - this.startX;
    let newX = this.currentX + deltaX;
    
    // Constrain movement
    newX = Math.max(-this.actionsWidth, Math.min(0, newX));
    
    this.content.style.transform = `translateX(${newX}px)`;
  }
  
  onEnd(e) {
    this.isDragging = false;
    this.content.style.transition = 'transform 0.2s ease-out';
    
    const deltaX = e.changedTouches[0].clientX - this.startX;
    
    if (this.isOpen) {
      // Closing
      if (deltaX > this.threshold) {
        this.close();
      } else {
        this.open();
      }
    } else {
      // Opening
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
  }
  
  close() {
    this.isOpen = false;
    this.content.style.transform = 'translateX(0)';
  }
}
```

### Pull-to-Refresh

```javascript
class PullToRefresh {
  constructor(options) {
    this.container = options.container;
    this.onRefresh = options.onRefresh;
    this.threshold = options.threshold || 80;
    
    this.startY = 0;
    this.currentY = 0;
    this.isPulling = false;
    this.isRefreshing = false;
    
    this.createIndicator();
    this.setupTouchHandlers();
  }
  
  createIndicator() {
    this.indicator = document.createElement('div');
    this.indicator.className = 'pull-indicator';
    this.indicator.innerHTML = `
      <div class="pull-arrow">↓</div>
      <div class="pull-text">Pull to refresh</div>
      <div class="pull-spinner" hidden></div>
    `;
    this.container.prepend(this.indicator);
  }
  
  setupTouchHandlers() {
    this.container.addEventListener('touchstart', this.onStart.bind(this));
    this.container.addEventListener('touchmove', this.onMove.bind(this));
    this.container.addEventListener('touchend', this.onEnd.bind(this));
  }
  
  onStart(e) {
    if (this.isRefreshing) return;
    if (this.container.scrollTop > 0) return;
    
    this.startY = e.touches[0].clientY;
    this.isPulling = true;
  }
  
  onMove(e) {
    if (!this.isPulling) return;
    
    this.currentY = e.touches[0].clientY;
    const pullDistance = Math.min(
      this.currentY - this.startY,
      this.threshold * 1.5
    );
    
    if (pullDistance > 0) {
      e.preventDefault();
      this.indicator.style.transform = `translateY(${pullDistance}px)`;
      
      if (pullDistance >= this.threshold) {
        this.indicator.querySelector('.pull-text').textContent = 'Release to refresh';
        this.indicator.classList.add('ready');
      } else {
        this.indicator.querySelector('.pull-text').textContent = 'Pull to refresh';
        this.indicator.classList.remove('ready');
      }
    }
  }
  
  async onEnd() {
    if (!this.isPulling) return;
    this.isPulling = false;
    
    const pullDistance = this.currentY - this.startY;
    
    if (pullDistance >= this.threshold) {
      this.isRefreshing = true;
      this.indicator.classList.add('refreshing');
      
      try {
        await this.onRefresh();
      } finally {
        this.isRefreshing = false;
        this.indicator.classList.remove('refreshing');
      }
    }
    
    this.indicator.style.transform = '';
    this.indicator.classList.remove('ready');
  }
}
```

---

## Gesture Discoverability

### Visual Hints

| Gesture | Visual Hint |
|---------|-------------|
| Swipe | Peek of hidden content, edge shadow |
| Long-press | Subtle scale on touch start |
| Drag | Handle icons (⋮⋮ or ≡) |
| Pinch | Zoom icon on first load |
| Pull-to-refresh | Arrow indicator, progress ring |

### Onboarding Patterns

```html
<!-- Gesture tutorial overlay -->
<div class="gesture-tutorial">
  <div class="gesture-demo">
    <div class="finger-indicator animate-swipe"></div>
    <p>Swipe left to delete</p>
  </div>
  <button class="dismiss-tutorial">Got it</button>
</div>

<style>
.finger-indicator {
  width: 40px;
  height: 40px;
  background: rgba(0,0,0,0.3);
  border-radius: 50%;
}

.animate-swipe {
  animation: swipeHint 2s infinite;
}

@keyframes swipeHint {
  0%, 100% { transform: translateX(0); opacity: 1; }
  50% { transform: translateX(-60px); opacity: 0.5; }
}
</style>
```

---

## Accessibility Alternatives

Every gesture must have a non-gesture alternative:

| Gesture | Alternative |
|---------|-------------|
| Swipe to delete | Delete button, context menu |
| Long-press menu | Visible overflow menu (⋮) |
| Pinch to zoom | Zoom controls (+/-) |
| Drag to reorder | Move up/down buttons |
| Pull-to-refresh | Refresh button |
| Swipe navigation | Visible buttons/tabs |

### WCAG 2.5.1 Compliance

```html
<!-- Swipeable item with accessible alternative -->
<li class="list-item">
  <div class="swipe-content">
    <span class="item-name">Item Name</span>
    <button class="action-button" aria-label="More actions">⋮</button>
  </div>
  <div class="swipe-actions" aria-hidden="true">
    <button class="action-delete">Delete</button>
  </div>
</li>

<!-- Context menu accessible via button -->
<menu class="context-menu" role="menu">
  <li role="menuitem"><button>Edit</button></li>
  <li role="menuitem"><button>Delete</button></li>
  <li role="menuitem"><button>Share</button></li>
</menu>
```

---

## Gesture Feedback

### Haptic Patterns

| Gesture | Haptic Type | When |
|---------|------------|------|
| Tap | Light impact | On touch up |
| Long-press | Medium impact | On threshold |
| Swipe complete | Light impact | On action trigger |
| Drag start | Selection | On drag begin |
| Drag reorder | Light impact | On position change |
| Error | Error notification | On invalid gesture |

### Visual Feedback

```css
/* Tap feedback */
.tappable {
  transition: transform 0.1s, opacity 0.1s;
}

.tappable:active {
  transform: scale(0.97);
  opacity: 0.8;
}

/* Long-press feedback */
.long-pressable:active {
  animation: longPressScale 0.5s forwards;
}

@keyframes longPressScale {
  0% { transform: scale(1); }
  100% { transform: scale(0.95); }
}

/* Drag feedback */
.dragging {
  opacity: 0.8;
  box-shadow: 0 8px 24px rgba(0,0,0,0.2);
  transform: scale(1.02);
}
```

---

## Key Takeaways

1. **Match platform conventions** — iOS/Android have different gesture expectations
2. **Avoid system gesture zones** — Don't override edge swipes
3. **Always provide alternatives** — Accessibility requires non-gesture options
4. **Give feedback** — Visual + haptic confirmation
5. **Teach gestures** — Onboarding or visual hints for non-obvious gestures
6. **Test on devices** — Gesture feel differs on real hardware
