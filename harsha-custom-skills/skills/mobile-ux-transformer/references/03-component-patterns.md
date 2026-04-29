# Component Transformation Patterns

> Desktop-to-mobile component mapping with implementation examples

## Universal Transformation Rules

### Core Principles

1. **Vertical over horizontal** — Mobile screens are taller than wide
2. **Tap over hover** — No hover states on touch devices
3. **Full-width over inline** — Maximize limited space
4. **Progressive over simultaneous** — Show one thing at a time
5. **Native over custom** — Use platform components when possible

---

## Data Tables → Cards / Lists

### When to Transform

| Table Characteristics | Recommendation |
|----------------------|----------------|
| 2-3 columns | Keep as table, make responsive |
| 4-5 columns | Transform to cards |
| 6+ columns | Prioritize columns, use expandable rows |
| Comparison data | Keep table with horizontal scroll |
| Scannable lists | Transform to list view |

### Card Transformation Pattern

**Desktop Table:**
```html
<table>
  <thead>
    <tr>
      <th>Order</th>
      <th>Date</th>
      <th>Customer</th>
      <th>Amount</th>
      <th>Status</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>#1234</td>
      <td>Jan 15, 2025</td>
      <td>John Doe</td>
      <td>$125.00</td>
      <td>Shipped</td>
    </tr>
  </tbody>
</table>
```

**Mobile Card:**
```html
<article class="order-card">
  <header class="card-header">
    <span class="order-id">#1234</span>
    <span class="status status--shipped">Shipped</span>
  </header>
  <div class="card-body">
    <p class="customer">John Doe</p>
    <p class="date">Jan 15, 2025</p>
  </div>
  <footer class="card-footer">
    <span class="amount">$125.00</span>
    <button class="card-action">View Details</button>
  </footer>
</article>
```

### CSS Implementation

```css
/* Responsive table to cards */
@media (max-width: 768px) {
  .responsive-table thead {
    display: none;
  }
  
  .responsive-table tbody tr {
    display: block;
    margin-bottom: 16px;
    padding: 16px;
    border: 1px solid var(--border);
    border-radius: 8px;
  }
  
  .responsive-table td {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid var(--border-light);
  }
  
  .responsive-table td::before {
    content: attr(data-label);
    font-weight: 600;
    color: var(--text-secondary);
  }
  
  .responsive-table td:last-child {
    border-bottom: none;
  }
}
```

---

## Modal Dialogs → Bottom Sheets

### Why Bottom Sheets

- **Thumb accessible** — Dismiss and interact from natural zone
- **Familiar pattern** — Users expect bottom sheets on mobile
- **Partial coverage** — Maintains context of underlying screen
- **Swipe dismissible** — Natural gesture to close

### Implementation

```html
<!-- Bottom Sheet Structure -->
<div class="bottom-sheet" role="dialog" aria-modal="true">
  <div class="sheet-backdrop"></div>
  <div class="sheet-content">
    <div class="sheet-handle" aria-hidden="true"></div>
    <header class="sheet-header">
      <h2>Select Option</h2>
      <button class="sheet-close" aria-label="Close">×</button>
    </header>
    <div class="sheet-body">
      <!-- Content -->
    </div>
  </div>
</div>
```

```css
.bottom-sheet {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
}

.sheet-backdrop {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
}

.sheet-content {
  position: relative;
  background: var(--surface);
  border-radius: 16px 16px 0 0;
  max-height: 90vh;
  overflow-y: auto;
  padding-bottom: env(safe-area-inset-bottom);
  animation: slideUp 0.3s ease-out;
}

.sheet-handle {
  width: 32px;
  height: 4px;
  background: var(--border);
  border-radius: 2px;
  margin: 8px auto 16px;
}

@keyframes slideUp {
  from { transform: translateY(100%); }
  to { transform: translateY(0); }
}
```

### Swipe-to-Dismiss JavaScript

```javascript
class BottomSheet {
  constructor(element) {
    this.element = element;
    this.content = element.querySelector('.sheet-content');
    this.startY = 0;
    this.currentY = 0;
    
    this.setupTouchHandlers();
  }
  
  setupTouchHandlers() {
    this.content.addEventListener('touchstart', this.onTouchStart.bind(this));
    this.content.addEventListener('touchmove', this.onTouchMove.bind(this));
    this.content.addEventListener('touchend', this.onTouchEnd.bind(this));
  }
  
  onTouchStart(e) {
    this.startY = e.touches[0].clientY;
  }
  
  onTouchMove(e) {
    this.currentY = e.touches[0].clientY;
    const deltaY = this.currentY - this.startY;
    
    // Only allow dragging down
    if (deltaY > 0) {
      this.content.style.transform = `translateY(${deltaY}px)`;
    }
  }
  
  onTouchEnd() {
    const deltaY = this.currentY - this.startY;
    
    if (deltaY > 100) {
      this.close();
    } else {
      this.content.style.transform = '';
    }
  }
  
  close() {
    this.content.style.transform = 'translateY(100%)';
    setTimeout(() => this.element.remove(), 300);
  }
}
```

---

## Dropdown Select → Native Picker / Action Sheet

### Platform-Specific Approach

| Platform | Recommendation |
|----------|---------------|
| iOS | Native `<select>` triggers wheel picker |
| Android | Native `<select>` triggers dropdown/dialog |
| Web (many options) | Custom full-screen picker |
| Web (few options) | Action sheet / radio buttons |

### Enhanced Select for Many Options

```html
<!-- Trigger button -->
<button class="select-trigger" aria-haspopup="listbox">
  <span class="select-value">Choose country</span>
  <svg class="select-arrow">...</svg>
</button>

<!-- Full-screen picker -->
<div class="fullscreen-picker" role="listbox">
  <header class="picker-header">
    <button class="picker-cancel">Cancel</button>
    <h2>Select Country</h2>
    <button class="picker-done">Done</button>
  </header>
  <div class="picker-search">
    <input type="search" placeholder="Search countries...">
  </div>
  <ul class="picker-options">
    <li role="option" aria-selected="false">Afghanistan</li>
    <li role="option" aria-selected="true">United States</li>
    <!-- ... -->
  </ul>
</div>
```

### Action Sheet for Few Options

```html
<!-- iOS-style action sheet -->
<div class="action-sheet" role="listbox">
  <div class="action-sheet-options">
    <button class="action-option" role="option">Take Photo</button>
    <button class="action-option" role="option">Choose from Library</button>
    <button class="action-option" role="option">Browse Files</button>
  </div>
  <button class="action-cancel">Cancel</button>
</div>
```

```css
.action-sheet {
  position: fixed;
  bottom: 0;
  left: 8px;
  right: 8px;
  padding-bottom: calc(8px + env(safe-area-inset-bottom));
  z-index: 1000;
}

.action-sheet-options {
  background: var(--surface);
  border-radius: 12px;
  overflow: hidden;
}

.action-option {
  display: block;
  width: 100%;
  padding: 16px;
  border: none;
  background: transparent;
  font-size: 17px;
  color: var(--primary);
  text-align: center;
}

.action-option:not(:last-child) {
  border-bottom: 1px solid var(--border);
}

.action-cancel {
  display: block;
  width: 100%;
  margin-top: 8px;
  padding: 16px;
  border: none;
  border-radius: 12px;
  background: var(--surface);
  font-size: 17px;
  font-weight: 600;
  color: var(--primary);
}
```

---

## Hover States → Tap States

### Transformation Rules

| Desktop Hover | Mobile Equivalent |
|--------------|-------------------|
| Tooltip on hover | Long-press or info icon |
| Hover preview | Tap to expand |
| Hover to reveal actions | Swipe to reveal |
| Hover dropdown | Tap to open menu |
| Hover highlight | Active/pressed state |

### CSS Implementation

```css
/* Desktop hover + Mobile active */
.interactive-element {
  transition: transform 0.1s ease, background-color 0.1s ease;
}

/* Desktop only hover */
@media (hover: hover) {
  .interactive-element:hover {
    background-color: var(--hover);
    transform: translateY(-2px);
  }
}

/* Mobile tap feedback */
.interactive-element:active {
  background-color: var(--active);
  transform: scale(0.98);
}

/* Remove tap highlight on iOS/Android */
.interactive-element {
  -webkit-tap-highlight-color: transparent;
}
```

### Tooltip Replacement

```html
<!-- Desktop: Hover tooltip -->
<button data-tooltip="More information">
  <svg>...</svg>
</button>

<!-- Mobile: Info button with bottom sheet -->
<button aria-label="Show information" class="info-trigger">
  <svg>ⓘ</svg>
</button>
```

---

## Multi-Column Layout → Single Column

### Responsive Grid Strategy

```css
/* Mobile-first single column */
.content-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: 1fr;
}

/* Tablet: 2 columns */
@media (min-width: 768px) {
  .content-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 24px;
  }
}

/* Desktop: 3-4 columns */
@media (min-width: 1024px) {
  .content-grid {
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 32px;
  }
}
```

### Sidebar → Tab or Accordion

```html
<!-- Desktop: Sidebar navigation -->
<aside class="sidebar">
  <nav>
    <a href="#overview">Overview</a>
    <a href="#details">Details</a>
    <a href="#reviews">Reviews</a>
  </nav>
</aside>

<!-- Mobile: Tab bar or segmented control -->
<nav class="mobile-tabs" role="tablist">
  <button role="tab" aria-selected="true">Overview</button>
  <button role="tab">Details</button>
  <button role="tab">Reviews</button>
</nav>
```

---

## Pagination → Infinite Scroll / Load More

### Decision Matrix

| Content Type | Recommendation |
|-------------|----------------|
| Feed/timeline | Infinite scroll |
| Search results | Load more button |
| Catalog browsing | Infinite scroll |
| Specific page needed | Keep pagination |

### Infinite Scroll Implementation

```javascript
class InfiniteScroll {
  constructor(options) {
    this.container = options.container;
    this.loadMore = options.loadMore;
    this.threshold = options.threshold || 200;
    this.loading = false;
    this.hasMore = true;
    
    this.setupObserver();
  }
  
  setupObserver() {
    // Create sentinel element
    this.sentinel = document.createElement('div');
    this.sentinel.className = 'scroll-sentinel';
    this.container.appendChild(this.sentinel);
    
    // Intersection Observer
    this.observer = new IntersectionObserver(
      entries => {
        if (entries[0].isIntersecting && !this.loading && this.hasMore) {
          this.load();
        }
      },
      { rootMargin: `${this.threshold}px` }
    );
    
    this.observer.observe(this.sentinel);
  }
  
  async load() {
    this.loading = true;
    this.showLoader();
    
    try {
      const { items, hasMore } = await this.loadMore();
      this.hasMore = hasMore;
      this.appendItems(items);
    } catch (error) {
      this.showError();
    }
    
    this.loading = false;
    this.hideLoader();
  }
  
  appendItems(items) {
    items.forEach(item => {
      this.container.insertBefore(item, this.sentinel);
    });
  }
}
```

### Load More Button Alternative

```html
<div class="results-container">
  <!-- Items -->
</div>

<div class="load-more-container">
  <p class="results-count">Showing 20 of 156 results</p>
  <button class="load-more-button">Load More</button>
</div>
```

---

## Horizontal Navigation → Bottom Tab Bar

### Implementation

```html
<nav class="bottom-nav" role="navigation" aria-label="Main">
  <a href="/" class="nav-item active" aria-current="page">
    <svg class="nav-icon" aria-hidden="true"><!-- Home icon --></svg>
    <span class="nav-label">Home</span>
  </a>
  <a href="/search" class="nav-item">
    <svg class="nav-icon" aria-hidden="true"><!-- Search icon --></svg>
    <span class="nav-label">Search</span>
  </a>
  <a href="/cart" class="nav-item">
    <svg class="nav-icon" aria-hidden="true"><!-- Cart icon --></svg>
    <span class="nav-label">Cart</span>
    <span class="badge">3</span>
  </a>
  <a href="/account" class="nav-item">
    <svg class="nav-icon" aria-hidden="true"><!-- Account icon --></svg>
    <span class="nav-label">Account</span>
  </a>
</nav>
```

```css
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 56px;
  padding-bottom: env(safe-area-inset-bottom);
  display: flex;
  justify-content: space-around;
  align-items: center;
  background: var(--surface);
  border-top: 1px solid var(--border);
  z-index: 1000;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-width: 64px;
  min-height: 48px;
  padding: 6px 12px;
  text-decoration: none;
  color: var(--text-secondary);
  position: relative;
}

.nav-item.active {
  color: var(--primary);
}

.nav-icon {
  width: 24px;
  height: 24px;
  margin-bottom: 4px;
}

.nav-label {
  font-size: 12px;
  font-weight: 500;
}

.badge {
  position: absolute;
  top: 4px;
  right: 8px;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  background: var(--error);
  color: white;
  font-size: 11px;
  font-weight: 600;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
}
```

---

## Side Panel → Full-Screen Overlay

### Transformation

```html
<!-- Desktop: Side panel -->
<aside class="side-panel">
  <h2>Filters</h2>
  <!-- Filter content -->
</aside>

<!-- Mobile: Full-screen overlay -->
<div class="fullscreen-overlay">
  <header class="overlay-header">
    <button class="overlay-close">Close</button>
    <h2>Filters</h2>
    <button class="overlay-apply">Apply</button>
  </header>
  <div class="overlay-content">
    <!-- Same filter content -->
  </div>
</div>
```

---

## Right-Click Menu → Long-Press Menu

### iOS-Style Context Menu

```javascript
let pressTimer;
const LONG_PRESS_DURATION = 500;

element.addEventListener('touchstart', (e) => {
  pressTimer = setTimeout(() => {
    showContextMenu(e.touches[0].clientX, e.touches[0].clientY);
    // Haptic feedback
    if (navigator.vibrate) {
      navigator.vibrate(10);
    }
  }, LONG_PRESS_DURATION);
});

element.addEventListener('touchend', () => {
  clearTimeout(pressTimer);
});

element.addEventListener('touchmove', () => {
  clearTimeout(pressTimer);
});
```

---

## Quick Reference Table

| Desktop Pattern | Mobile Pattern | Key Difference |
|----------------|----------------|----------------|
| Data table | Cards / List view | Vertical stacking |
| Modal dialog | Bottom sheet | Thumb accessible |
| Dropdown select | Native picker / Action sheet | Platform native |
| Hover tooltip | Long-press / Info button | No hover on touch |
| Multi-column | Single column | Screen width |
| Pagination | Infinite scroll / Load more | Continuous flow |
| Horizontal nav | Bottom tab bar | Thumb zone |
| Side panel | Full-screen overlay | Space constraint |
| Right-click | Long-press menu | Touch equivalent |
| Keyboard shortcuts | Gestures | Touch equivalent |
