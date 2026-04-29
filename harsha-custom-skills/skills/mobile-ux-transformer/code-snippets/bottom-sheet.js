/**
 * Bottom Sheet Component
 * Mobile-optimized modal alternative
 */

class BottomSheet {
  constructor(options = {}) {
    this.options = {
      snapPoints: options.snapPoints || [0.5, 1],
      initialSnap: options.initialSnap || 0,
      dismissible: options.dismissible !== false,
      overlay: options.overlay !== false,
      onOpen: options.onOpen || (() => {}),
      onClose: options.onClose || (() => {}),
      onSnap: options.onSnap || (() => {})
    };
    
    this.isOpen = false;
    this.currentSnap = this.options.initialSnap;
    this.startY = 0;
    this.currentY = 0;
    this.isDragging = false;
    
    this.create();
    this.setupEventListeners();
  }
  
  create() {
    // Overlay
    this.overlay = document.createElement('div');
    this.overlay.className = 'bottom-sheet-overlay';
    this.overlay.setAttribute('aria-hidden', 'true');
    
    // Sheet container
    this.sheet = document.createElement('div');
    this.sheet.className = 'bottom-sheet';
    this.sheet.setAttribute('role', 'dialog');
    this.sheet.setAttribute('aria-modal', 'true');
    this.sheet.innerHTML = `
      <div class="bottom-sheet-handle" aria-hidden="true">
        <span class="handle-bar"></span>
      </div>
      <div class="bottom-sheet-content"></div>
    `;
    
    this.handle = this.sheet.querySelector('.bottom-sheet-handle');
    this.content = this.sheet.querySelector('.bottom-sheet-content');
    
    document.body.appendChild(this.overlay);
    document.body.appendChild(this.sheet);
    
    this.injectStyles();
  }
  
  injectStyles() {
    if (document.getElementById('bottom-sheet-styles')) return;
    
    const styles = document.createElement('style');
    styles.id = 'bottom-sheet-styles';
    styles.textContent = `
      .bottom-sheet-overlay {
        position: fixed;
        inset: 0;
        background: rgba(0, 0, 0, 0.4);
        opacity: 0;
        visibility: hidden;
        transition: opacity 0.3s, visibility 0.3s;
        z-index: 999;
      }
      
      .bottom-sheet-overlay.visible {
        opacity: 1;
        visibility: visible;
      }
      
      .bottom-sheet {
        position: fixed;
        left: 0;
        right: 0;
        bottom: 0;
        max-height: 90vh;
        background: var(--bg-elevated, #fff);
        border-radius: 16px 16px 0 0;
        transform: translateY(100%);
        transition: transform 0.3s cubic-bezier(0.32, 0.72, 0, 1);
        z-index: 1000;
        display: flex;
        flex-direction: column;
        box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.15);
      }
      
      .bottom-sheet.open {
        transform: translateY(0);
      }
      
      .bottom-sheet.dragging {
        transition: none;
      }
      
      .bottom-sheet-handle {
        padding: 12px;
        cursor: grab;
        display: flex;
        justify-content: center;
        flex-shrink: 0;
      }
      
      .bottom-sheet-handle:active {
        cursor: grabbing;
      }
      
      .handle-bar {
        width: 36px;
        height: 5px;
        background: var(--border-default, #d1d5db);
        border-radius: 3px;
      }
      
      .bottom-sheet-content {
        flex: 1;
        overflow-y: auto;
        overscroll-behavior: contain;
        padding: 0 16px 16px;
        padding-bottom: calc(16px + env(safe-area-inset-bottom, 0));
      }
      
      @media (prefers-color-scheme: dark) {
        .bottom-sheet {
          background: #1c1c1e;
        }
        
        .bottom-sheet-overlay {
          background: rgba(0, 0, 0, 0.6);
        }
        
        .handle-bar {
          background: #48484a;
        }
      }
      
      @media (prefers-reduced-motion: reduce) {
        .bottom-sheet,
        .bottom-sheet-overlay {
          transition: none;
        }
      }
    `;
    document.head.appendChild(styles);
  }
  
  setupEventListeners() {
    // Handle drag
    this.handle.addEventListener('touchstart', this.onDragStart.bind(this), { passive: true });
    document.addEventListener('touchmove', this.onDragMove.bind(this), { passive: false });
    document.addEventListener('touchend', this.onDragEnd.bind(this));
    
    // Overlay click
    if (this.options.dismissible) {
      this.overlay.addEventListener('click', () => this.close());
    }
    
    // Escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.isOpen && this.options.dismissible) {
        this.close();
      }
    });
  }
  
  onDragStart(e) {
    this.isDragging = true;
    this.startY = e.touches[0].clientY;
    this.sheetHeight = this.sheet.offsetHeight;
    this.sheet.classList.add('dragging');
  }
  
  onDragMove(e) {
    if (!this.isDragging) return;
    
    this.currentY = e.touches[0].clientY;
    const deltaY = this.currentY - this.startY;
    
    if (deltaY > 0) { // Only allow dragging down
      e.preventDefault();
      this.sheet.style.transform = `translateY(${deltaY}px)`;
      
      // Update overlay opacity
      const progress = 1 - (deltaY / this.sheetHeight);
      this.overlay.style.opacity = Math.max(0, progress);
    }
  }
  
  onDragEnd() {
    if (!this.isDragging) return;
    
    this.isDragging = false;
    this.sheet.classList.remove('dragging');
    this.sheet.style.transform = '';
    this.overlay.style.opacity = '';
    
    const deltaY = this.currentY - this.startY;
    const velocity = deltaY / (Date.now() - this.dragStartTime || 1);
    
    // Close if dragged more than 25% or with velocity
    if (deltaY > this.sheetHeight * 0.25 || velocity > 0.5) {
      this.close();
    } else {
      // Snap back
      this.sheet.style.transform = 'translateY(0)';
    }
  }
  
  setContent(html) {
    this.content.innerHTML = html;
    return this;
  }
  
  open() {
    if (this.isOpen) return;
    
    this.isOpen = true;
    this.previousActiveElement = document.activeElement;
    
    // Prevent body scroll
    document.body.style.overflow = 'hidden';
    
    // Show
    if (this.options.overlay) {
      this.overlay.classList.add('visible');
    }
    this.sheet.classList.add('open');
    
    // Focus first focusable element
    requestAnimationFrame(() => {
      const focusable = this.content.querySelector('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
      if (focusable) focusable.focus();
    });
    
    // Haptic feedback
    if (navigator.vibrate) {
      navigator.vibrate(10);
    }
    
    this.options.onOpen();
    return this;
  }
  
  close() {
    if (!this.isOpen) return;
    
    this.isOpen = false;
    
    // Hide
    this.overlay.classList.remove('visible');
    this.sheet.classList.remove('open');
    
    // Restore body scroll
    document.body.style.overflow = '';
    
    // Restore focus
    if (this.previousActiveElement) {
      this.previousActiveElement.focus();
    }
    
    this.options.onClose();
    return this;
  }
  
  destroy() {
    this.overlay.remove();
    this.sheet.remove();
  }
}

// Export
export default BottomSheet;

// Usage example:
/*
const sheet = new BottomSheet({
  dismissible: true,
  onClose: () => console.log('Sheet closed')
});

sheet.setContent(`
  <h2>Choose an option</h2>
  <button class="option-btn">Option 1</button>
  <button class="option-btn">Option 2</button>
  <button class="option-btn">Cancel</button>
`).open();
*/
